from PIL import Image
import re
from datetime import datetime
import os
import logging
import base64

logger = logging.getLogger(__name__)

class OCRService:
    def __init__(self):
        # Load environment variables - try multiple paths
        from dotenv import load_dotenv
        from pathlib import Path
        
        # Try to load .env from current directory and parent directories
        current_dir = Path(__file__).parent.parent  # backend directory
        env_paths = [
            current_dir / ".env",
            current_dir.parent / ".env",
            Path(".env"),  # Current working directory
        ]
        
        env_loaded = False
        for env_path in env_paths:
            if env_path.exists():
                load_dotenv(dotenv_path=env_path)
                env_loaded = True
                logger.debug(f"Loaded .env from: {env_path}")
                break
        
        if not env_loaded:
            # Try default load_dotenv() which searches current directory and parents
            try:
                load_dotenv()
            except Exception as e:
                logger.debug(f"Could not load .env file: {e}")
        
        # Check for API key first (preferred method)
        self.api_key = os.getenv("GOOGLE_CLOUD_VISION_API_KEY")
        self.use_google_vision = False
        self.client = None
        
        if self.api_key:
            # Use API key authentication via REST API
            self.use_google_vision = True
            logger.info("✅ Google Cloud Vision API key found - using REST API")
        else:
            # Fallback to service account credentials
            try:
                from google.cloud import vision
                self.client = vision.ImageAnnotatorClient()
                self.use_google_vision = True
                logger.info("✅ Google Cloud Vision initialized with service account")
            except Exception as e:
                logger.warning(f"⚠️ Google Cloud Vision not available: {str(e)}")
                self.use_google_vision = False
        
        # Try to import pytesseract
        try:
            import pytesseract
            self.pytesseract = pytesseract
            self.use_tesseract = True
            logger.info("✅ Pytesseract initialized successfully")
        except ImportError:
            logger.warning("⚠️ Pytesseract not available")
            self.use_tesseract = False
        except Exception as e:
            logger.warning(f"⚠️ Pytesseract initialization error: {str(e)}")
            self.use_tesseract = False
    
    def extract_text(self, image_path):
        """Extract text from image using OCR"""
        if self.use_google_vision:
            return self._extract_text_google_vision(image_path)
        elif self.use_tesseract:
            return self._extract_text_pytesseract(image_path)
        else:
            # Fallback: use simple image analysis
            return self._extract_text_fallback(image_path)
    
    def _extract_text_google_vision(self, image_path):
        """Use Google Cloud Vision API"""
        try:
            if self.api_key:
                # Use REST API with API key
                return self._extract_text_google_vision_rest(image_path)
            else:
                # Use client library with service account
                return self._extract_text_google_vision_client(image_path)
        except Exception as e:
            logger.error(f"❌ Google Vision API error: {str(e)}")
            return self._extract_text_pytesseract(image_path) if self.use_tesseract else []
    
    def _extract_text_google_vision_rest(self, image_path):
        """Use Google Cloud Vision REST API with API key"""
        import httpx
        
        # Read and encode image
        with open(image_path, 'rb') as image_file:
            image_content = image_file.read()
        
        image_base64 = base64.b64encode(image_content).decode('utf-8')
        
        # Prepare request
        url = f"https://vision.googleapis.com/v1/images:annotate?key={self.api_key}"
        payload = {
            "requests": [
                {
                    "image": {
                        "content": image_base64
                    },
                    "features": [
                        {
                            "type": "TEXT_DETECTION"
                        }
                    ]
                }
            ]
        }
        
        # Make API request
        with httpx.Client(timeout=30.0) as client:
            response = client.post(url, json=payload)
            response.raise_for_status()
            result = response.json()
        
        # Extract text annotations
        texts = []
        if "responses" in result and len(result["responses"]) > 0:
            text_annotations = result["responses"][0].get("textAnnotations", [])
            if text_annotations:
                # First annotation is full text, rest are individual blocks
                full_text = text_annotations[0].get("description", "")
                texts = [full_text] + [ann.get("description", "") for ann in text_annotations[1:]]
        
        logger.info(f"📝 Google Vision extracted {len(texts)} text blocks")
        logger.debug(f"📄 Full text:\n{texts[0] if texts else 'None'}")
        
        return texts
    
    def _extract_text_google_vision_client(self, image_path):
        """Use Google Cloud Vision client library with service account"""
        from google.cloud import vision
        
        with open(image_path, 'rb') as image_file:
            content = image_file.read()
        
        image = vision.Image(content=content)
        response = self.client.text_detection(image=image)
        
        # Get all text annotations
        texts = []
        if response.text_annotations:
            # First annotation is full text, rest are individual blocks
            full_text = response.text_annotations[0].description
            texts = [full_text] + [annotation.description for annotation in response.text_annotations[1:]]
        
        logger.info(f"📝 Google Vision extracted {len(texts)} text blocks")
        logger.debug(f"📄 Full text:\n{texts[0] if texts else 'None'}")
        
        return texts
    
    def _extract_text_pytesseract(self, image_path):
        """Use pytesseract for local OCR"""
        try:
            from PIL import Image
            img = Image.open(image_path)
            # Vietnamese language support
            text = self.pytesseract.image_to_string(img, lang='vie+eng')
            return text.split('\n')
        except Exception as e:
            print(f"Pytesseract error: {str(e)}")
            return []
    
    def _extract_text_fallback(self, image_path):
        """Fallback when no OCR available"""
        try:
            from PIL import Image, ImageEnhance, ImageFilter
            
            img = Image.open(image_path)
            
            # Enhance image for better readability
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(2)
            
            enhancer = ImageEnhance.Sharpness(img)
            img = enhancer.enhance(2)
            
            # Note: This is just preprocessing, actual OCR still needed
            # Return empty - user should install pytesseract or use Google Vision
            return []
        except:
            return []
    
    def parse_invoice(self, image_path):
        """Parse invoice from image and extract structured data"""
        try:
            # Validate image exists
            img = Image.open(image_path)
            img.verify()
        except Exception as e:
            print(f"Image validation error: {str(e)}")
        
        # Extract text from image
        texts = self.extract_text(image_path)
        
        # If no OCR results, return defaults
        if not texts:
            return {
                "invoice_number": f"INV{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "date": datetime.now().strftime("%Y-%m-%d"),
                "subtotal": 0.0,
                "vat": 0.0,
                "total": 0.0,
                "seller_name": "Unknown",
                "seller_phone": None,
                "seller_address": None,
                "items": [],
                "raw_text": "OCR not available - please install Tesseract or Google Cloud Vision",
                "error": "OCR_NOT_CONFIGURED"
            }
        
        # Get full text for parsing
        full_text = texts[0] if texts else ""
        text_lines = full_text.split('\n') if full_text else []
        
        # Parse extracted text with structured line-by-line approach
        invoice_data = self._parse_structured_invoice(texts, full_text)
        
        # Fallback to old method if structured parsing didn't work well
        if invoice_data['total'] == 0 and invoice_data['subtotal'] == 0:
            logger.warning("⚠️ Structured parsing failed, using fallback methods")
            invoice_data = {
                "invoice_number": self._extract_invoice_number(texts),
                "date": self._extract_date(texts),
                "subtotal": self._extract_subtotal(texts),
                "vat": self._extract_vat(texts),
                "total": self._extract_total(texts),
                "seller_name": self._extract_seller(texts),
                "seller_phone": self._extract_phone(texts),
                "seller_address": self._extract_address(texts),
                "items": self._extract_items(texts),
                "raw_text": full_text
            }
        
        # Log extracted amounts for debugging
        logger.info(f"📊 Extracted amounts - Subtotal: {invoice_data['subtotal']}, VAT: {invoice_data['vat']}, Total: {invoice_data['total']}")
        
        # Final validation and correction
        # If total seems wrong (too small or 0), try to recalculate
        if invoice_data['total'] == 0 or (invoice_data['subtotal'] > 0 and invoice_data['total'] < invoice_data['subtotal']):
            if invoice_data['subtotal'] > 0:
                calculated_total = invoice_data['subtotal'] + invoice_data['vat']
                if calculated_total > 0:
                    logger.warning(f"⚠️ Total was {invoice_data['total']}, recalculating from subtotal + VAT: {calculated_total}")
                    invoice_data['total'] = calculated_total
        
        # Ensure total is at least subtotal if both exist
        if invoice_data['subtotal'] > 0 and invoice_data['total'] > 0 and invoice_data['total'] < invoice_data['subtotal']:
            logger.warning(f"⚠️ Total ({invoice_data['total']}) is less than subtotal ({invoice_data['subtotal']}), using subtotal + VAT")
            invoice_data['total'] = invoice_data['subtotal'] + invoice_data['vat']
        
        return invoice_data
    
    def _parse_structured_invoice(self, texts, full_text):
        """Parse invoice using structured line-by-line approach for better accuracy"""
        invoice_data = {
            "invoice_number": None,
            "date": None,
            "subtotal": 0.0,
            "vat": 0.0,
            "total": 0.0,
            "seller_name": None,
            "seller_phone": None,
            "seller_address": None,
            "items": [],
            "raw_text": full_text
        }
        
        if not texts or not full_text:
            return invoice_data
        
        text_lines = full_text.split('\n')
        
        # Parse line by line
        for i, line in enumerate(text_lines):
            line = line.strip()
            if not line:
                continue
            
            line_lower = line.lower()
            
            # Extract invoice number
            if not invoice_data['invoice_number']:
                invoice_num = self._extract_invoice_number_from_line(line)
                if invoice_num:
                    invoice_data['invoice_number'] = invoice_num
            
            # Extract date
            if not invoice_data['date']:
                date_str = self._extract_date_from_line(line)
                if date_str:
                    invoice_data['date'] = date_str
            
            # Extract seller name (usually in first few lines)
            if not invoice_data['seller_name'] and i < 10:
                seller = self._extract_seller_from_line(line, i)
                if seller:
                    invoice_data['seller_name'] = seller
            
            # Extract phone
            if not invoice_data['seller_phone']:
                phone = self._extract_phone_from_line(line)
                if phone:
                    invoice_data['seller_phone'] = phone
            
            # Extract address
            if not invoice_data['seller_address']:
                address = self._extract_address_from_line(line)
                if address:
                    invoice_data['seller_address'] = address
            
            # Extract subtotal - "Tổng tiền hàng: 63,325"
            if 'tổng tiền hàng' in line_lower and invoice_data['subtotal'] == 0:
                # Use same pattern matching as total
                patterns = [
                    r'tổng\s*tiền\s*hàng[\s:]*([\d]{1,3}(?:[,\.][\d]{3})+)\s*(?:vnđ|đ)?',  # 63,325 or 63.325
                    r'tổng\s*tiền\s*hàng[\s:]*([\d]{4,8})\s*(?:vnđ|đ)?',  # 63325 (no separator)
                    r'tổng\s*tiền\s*hàng[\s:]*([\d,\.]+)',  # Any number format
                ]
                
                for pattern in patterns:
                    match = re.search(pattern, line, re.IGNORECASE)
                    if match:
                        amount_str = match.group(1).strip()
                        amount_str = re.sub(r'[^\d,\.]', '', amount_str)
                        amount = self._normalize_amount(amount_str)
                        if amount > 0 and 1000 <= amount <= 100000000:
                            invoice_data['subtotal'] = amount
                            logger.info(f"✅ Found subtotal on line {i}: {amount} from '{line}' (extracted: '{amount_str}')")
                            break
                else:
                    # Fallback
                    amount = self._extract_amount_from_line(line)
                    if amount > 0 and 1000 <= amount <= 100000000:
                        invoice_data['subtotal'] = amount
                        logger.info(f"✅ Found subtotal on line {i}: {amount} from '{line}' (fallback)")
            
            # Extract VAT - "VAT: 5,066" or "VAT 5,066"
            if (('vat' in line_lower and 'tổng' not in line_lower) or ('thuế' in line_lower and 'gtgt' in line_lower)) and invoice_data['vat'] == 0:
                # Use same pattern matching as total
                patterns = [
                    r'(?:vat|thuế\s*gtgt|thuế\s*vat)[\s:]*([\d]{1,3}(?:[,\.][\d]{3})+)\s*(?:vnđ|đ)?',  # 5,066 or 5.066
                    r'(?:vat|thuế\s*gtgt|thuế\s*vat)[\s:]*([\d]{3,6})\s*(?:vnđ|đ)?',  # 5066 (no separator)
                    r'(?:vat|thuế)[\s:]*([\d,\.]+)',  # Any number format
                ]
                
                amount_found = False
                for pattern in patterns:
                    match = re.search(pattern, line, re.IGNORECASE)
                    if match:
                        amount_str = match.group(1).strip()
                        amount_str = re.sub(r'[^\d,\.]', '', amount_str)
                        amount = self._normalize_amount(amount_str)
                        if amount > 0 and amount <= 10000000:  # VAT should be reasonable
                            invoice_data['vat'] = amount
                            logger.info(f"✅ Found VAT on line {i}: {amount} from '{line}' (extracted: '{amount_str}')")
                            amount_found = True
                            break
                
                if not amount_found:
                    # Fallback
                    amount = self._extract_amount_from_line(line)
                    if amount > 0 and amount <= 10000000:
                        invoice_data['vat'] = amount
                        logger.info(f"✅ Found VAT on line {i}: {amount} from '{line}' (fallback)")
            
            # Extract total - "Tổng Cộng: 68,391" (should be last)
            # Make sure we get the LAST occurrence (grand total)
            if 'tổng cộng' in line_lower:
                # Method 1: Direct pattern match - find number immediately after "Tổng Cộng"
                # Try multiple patterns to catch different formats, prioritize comma format
                patterns = [
                    r'tổng\s*cộng[\s:]*([\d]{1,3},\d{3})\s*(?:vnđ|đ)?',  # 68,391 (comma format - Vietnamese)
                    r'tổng\s*cộng[\s:]*([\d]{1,3}\.\d{3})\s*(?:vnđ|đ)?',  # 68.391 (dot format)
                    r'tổng\s*cộng[\s:]*([\d]{4,6})\s*(?:vnđ|đ)?',  # 68391 (no separator, 4-6 digits)
                    r'tổng\s*cộng[\s:]*([\d]{1,3}(?:[,\.][\d]{3})+)\s*(?:vnđ|đ)?',  # Any format with separators
                    r'tổng\s*cộng[\s:]*([\d,\.]+)',  # Any number format (fallback)
                ]
                
                amount_found = False
                for pattern in patterns:
                    match = re.search(pattern, line, re.IGNORECASE)
                    if match:
                        amount_str = match.group(1).strip()
                        # Clean the amount string - keep only digits, comma, and dot
                        amount_str = re.sub(r'[^\d,\.]', '', amount_str)
                        
                        # Debug log
                        logger.debug(f"🔍 Parsing total from line {i}: '{line}' -> extracted: '{amount_str}'")
                        
                        amount = self._normalize_amount(amount_str)
                        
                        if amount > 0 and 1000 <= amount <= 100000000:  # Reasonable range
                            invoice_data['total'] = amount
                            logger.info(f"✅ Found total on line {i}: {amount} from '{line}' (extracted: '{amount_str}')")
                            amount_found = True
                            break
                
                # Method 2: If pattern matching failed, try extracting from line
                if not amount_found:
                    amount = self._extract_amount_from_line(line)
                    if amount > 0 and 1000 <= amount <= 100000000:
                        invoice_data['total'] = amount
                        logger.info(f"✅ Found total on line {i}: {amount} from '{line}' (fallback extraction)")
                    else:
                        logger.warning(f"⚠️ Could not parse total from line {i}: '{line}'")
        
        # Extract items (between header and totals)
        invoice_data['items'] = self._extract_items_structured(text_lines)
        
        # Set defaults if not found
        if not invoice_data['invoice_number']:
            invoice_data['invoice_number'] = self._extract_invoice_number(texts)
        if not invoice_data['date']:
            invoice_data['date'] = self._extract_date(texts)
        if not invoice_data['seller_name']:
            invoice_data['seller_name'] = self._extract_seller(texts)
        
        # Final validation: if total is 0 but we have subtotal and VAT, calculate total
        if invoice_data['total'] == 0 and invoice_data['subtotal'] > 0:
            calculated_total = invoice_data['subtotal'] + invoice_data['vat']
            if calculated_total > 0:
                logger.warning(f"⚠️ Total was 0, calculating from subtotal + VAT: {calculated_total}")
                invoice_data['total'] = calculated_total
        
        # Log final parsed data for debugging
        logger.info(f"📋 Final parsed invoice: Total={invoice_data['total']}, Subtotal={invoice_data['subtotal']}, VAT={invoice_data['vat']}")
        
        return invoice_data
    
    def _extract_invoice_number_from_line(self, line):
        """Extract invoice number from a single line - exclude phone numbers"""
        # First check if line contains invoice number patterns
        patterns = [
            r'\b(HD\d{6,})\b',  # HD040334
            r'\b(HĐ\d{6,})\b',  # HĐ040334
            r'(?:HD|HĐ)[\s:]*(\d{6,})',  # HD: 040334
            r'(?:phiếu|hóa đơn|bill|receipt)[\s#:\-]*([A-Z]{2}\d{6,})',  # Phiếu HD040334
        ]
        
        for pattern in patterns:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                invoice_num = match.group(1) if match.lastindex else match.group(0)
                # Make sure it's not a phone number (phone numbers are usually 10-11 digits starting with 0 or +84)
                if not re.match(r'^(\+84|84|0)\d{9,10}$', invoice_num):
                    return invoice_num.strip()
        
        return None
    
    def _extract_date_from_line(self, line):
        """Extract date from a single line"""
        patterns = [
            r'(\d{1,2})[/\-\.](\d{1,2})[/\-\.](\d{4})',
            r'ngày[\s:]*(\d{1,2})[/\-\.](\d{1,2})[/\-\.](\d{4})',
        ]
        for pattern in patterns:
            match = re.search(pattern, line)
            if match:
                try:
                    day, month, year = match.groups()[:3]
                    return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                except:
                    pass
        return None
    
    def _extract_seller_from_line(self, line, line_index):
        """Extract seller name from a line"""
        # Skip if looks like header, date, phone, or number
        if (re.match(r'^\d+', line) or 
            re.match(r'^\d{1,2}[/\-\.]', line) or
            re.match(r'^\+?\d{8,}', line) or
            re.search(r'(phiếu|hóa đơn|bill|receipt|địa chỉ|address)', line, re.IGNORECASE) or
            len(line) < 3):
            return None
        
        # Return if looks like business name (has letters, reasonable length)
        if re.search(r'[A-Za-zÀ-ỹ]', line) and 3 <= len(line) <= 100:
            return line.strip()
        return None
    
    def _extract_phone_from_line(self, line):
        """Extract phone from a line"""
        patterns = [
            r'\+?84[\s\-]?(\d{9,10})',
            r'0(\d{9,10})',
        ]
        for pattern in patterns:
            match = re.search(pattern, line)
            if match:
                phone = match.group(0).strip()
                phone = re.sub(r'[\s\-]', '', phone)
                return phone
        return None
    
    def _extract_address_from_line(self, line):
        """Extract address from a line"""
        if any(kw in line.lower() for kw in ['địa chỉ', 'address', 'đường', 'phố']):
            address = re.sub(r'^(địa chỉ|address)[:\-]?\s*', '', line, flags=re.IGNORECASE)
            if len(address.strip()) > 5:
                return address.strip()
        return None
    
    def _extract_amount_from_line(self, line):
        """Extract amount from a line containing amount keywords - avoid concatenating multiple numbers"""
        # Remove common prefixes/suffixes
        line_clean = re.sub(r'^(tổng\s*cộng|tổng\s*tiền\s*hàng|vat|thuế)[\s:]*', '', line, flags=re.IGNORECASE)
        line_clean = re.sub(r'\s*(vnđ|đ|dong)\s*$', '', line_clean, flags=re.IGNORECASE)
        line_clean = line_clean.strip()
        
        # Priority: Look for Vietnamese number format with thousand separators first
        # Pattern 1: Number with comma separator (68,391)
        comma_pattern = r'([\d]{1,3}(?:,\d{3})+)'
        comma_matches = re.findall(comma_pattern, line_clean)
        if comma_matches:
            for match in comma_matches:
                amount = self._normalize_amount(match)
                if 1000 <= amount <= 100000000:
                    return amount
        
        # Pattern 2: Number with dot separator (68.391)
        dot_pattern = r'([\d]{1,3}(?:\.\d{3})+)'
        dot_matches = re.findall(dot_pattern, line_clean)
        if dot_matches:
            for match in dot_matches:
                amount = self._normalize_amount(match)
                if 1000 <= amount <= 100000000:
                    return amount
        
        # Pattern 3: Plain number without separators (68391)
        plain_pattern = r'(\d{4,8})'  # 4-8 digits for reasonable amounts
        plain_matches = re.findall(plain_pattern, line_clean)
        if plain_matches:
            amounts = []
            for match in plain_matches:
                amount = float(match)
                if 1000 <= amount <= 100000000:
                    amounts.append(amount)
            if amounts:
                return max(amounts)
        
        # Pattern 4: Split by spaces/colons and find the first reasonable number
        parts = re.split(r'[\s:]+', line_clean)
        for part in parts:
            part = part.strip()
            # Try to find number in this part
            num_match = re.search(r'([\d,\.]{4,})', part)
            if num_match:
                amount = self._normalize_amount(num_match.group(1))
                if 1000 <= amount <= 100000000:
                    return amount
        
        return 0.0
    
    def _extract_items_structured(self, text_lines):
        """Extract items using structured approach"""
        items = []
        in_items_section = False
        items_started = False
        
        # Find where items section starts (usually after header, before totals)
        for i, line in enumerate(text_lines):
            line = line.strip()
            if not line:
                continue
            
            line_lower = line.lower()
            
            # Skip header lines
            if i < 5:
                continue
            
            # Check if we've reached totals section
            if any(keyword in line_lower for keyword in ['tổng tiền hàng', 'vat', 'thuế', 'tổng cộng']):
                break
            
            # Try to parse as item
            item = self._parse_item_line_structured(line)
            if item:
                items.append(item)
                items_started = True
        
        return items
    
    def _parse_item_line_structured(self, line):
        """Parse a single line as an item with better structure"""
        line = line.strip()
        if len(line) < 5:
            return None
        
        # Skip if looks like header, date, or other non-item
        if (re.match(r'^\d{1,2}[/\-\.]\d{1,2}', line) or  # Date
            re.match(r'^\+?\d{8,}', line) or  # Phone
            re.search(r'(phiếu|hóa đơn|bill|receipt|tổng|vat|thuế)', line, re.IGNORECASE)):
            return None
        
        # Extract all numbers from the line
        numbers = re.findall(r'([\d\s,\.]+)', line)
        if not numbers:
            return None
        
        # Parse amounts
        amounts = []
        for num_str in numbers:
            amount = self._normalize_amount(num_str)
            if amount > 0:
                amounts.append(amount)
        
        if not amounts:
            return None
        
        # Last amount is usually the total for this item
        item_total = amounts[-1]
        
        # Try to find quantity (usually first number or number with 'x')
        quantity = 1.0
        qty_match = re.search(r'(\d+(?:\.\d+)?)\s*x\s*', line, re.IGNORECASE)
        if qty_match:
            try:
                quantity = float(qty_match.group(1))
            except:
                pass
        
        # Unit price = total / quantity
        unit_price = item_total / quantity if quantity > 0 else item_total
        
        # If we have multiple amounts, second-to-last might be unit price
        if len(amounts) >= 2:
            unit_price = amounts[-2]
        
        # Extract item name (everything except numbers and common separators)
        name = line
        # Remove amounts
        for num_str in numbers:
            name = name.replace(num_str, '', 1)
        # Remove quantity markers
        name = re.sub(r'\d+\s*x\s*', '', name, flags=re.IGNORECASE)
        name = re.sub(r'\s*=\s*', ' ', name)
        name = re.sub(r'\s+', ' ', name).strip()
        
        # Clean up name
        name = re.sub(r'^[\d\.\s\-]+', '', name)  # Remove leading numbers
        name = name.strip()
        
        if len(name) < 2:
            return None
        
        return {
            "name": name,
            "quantity": quantity,
            "unit_price": unit_price,
            "amount": item_total
        }
    
    def _extract_invoice_number(self, texts):
        """Extract invoice/receipt number from text - exclude phone numbers"""
        if not texts:
            return f"INV{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        combined_text = " ".join(texts)
        full_text = texts[0] if texts else ""
        text_lines = full_text.split('\n') if full_text else []
        
        # First try line-by-line for better accuracy
        for line in text_lines[:20]:  # Check first 20 lines
            invoice_num = self._extract_invoice_number_from_line(line)
            if invoice_num:
                return invoice_num
        
        # Fallback to pattern matching on combined text
        patterns = [
            r'\b((?:HD|HĐ|INV|BILL)[\s:]*[A-Z0-9]{6,})\b',  # HD040334 format (with prefix)
            r'\b([A-Z]{2}\d{6,})\b',  # Format like HD040334 (without prefix in text)
            r'(?:HD|HĐ|INV|BILL)[\s:]*([A-Z0-9]{6,})',  # HD:040334 format
            r'(?:phiếu|hóa đơn|biên lai|receipt|bill)[\s#:\-]*([A-Z0-9\-]{6,})',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, combined_text, re.IGNORECASE)
            for match in matches:
                invoice_num = match.strip() if isinstance(match, str) else match[0].strip()
                # Exclude phone numbers (10-11 digits starting with 0, 84, or +84)
                if not re.match(r'^(\+84|84|0)?\d{9,11}$', invoice_num):
                    if len(invoice_num) >= 6:  # Minimum length
                        return invoice_num
        
        return f"INV{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    def _extract_date(self, texts):
        """Extract date from invoice text - supports Vietnamese formats"""
        if not texts:
            return datetime.now().strftime("%Y-%m-%d")
        
        combined_text = " ".join(texts)
        
        # Vietnamese date patterns
        patterns = [
            # DD/MM/YYYY or DD-MM-YYYY or DD.MM.YYYY
            r'(\d{1,2})[/\-\.](\d{1,2})[/\-\.](\d{4}|\d{2})',
            # With time: DD/MM/YYYY HH:MM
            r'(\d{1,2})[/\-](\d{1,2})[/\-](\d{4})\s+\d{1,2}:\d{2}',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, combined_text)
            if match:
                try:
                    day, month, year = match.groups()[0:3]
                    year = year if len(year) == 4 else "20" + year
                    # Convert DD/MM/YYYY to YYYY-MM-DD
                    return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                except:
                    pass
        
        return datetime.now().strftime("%Y-%m-%d")
    
    def _normalize_amount(self, amount_str):
        """Normalize Vietnamese number format to float - prevent concatenating multiple numbers"""
        if not amount_str:
            return 0.0
        
        # Convert to string and clean
        amount_str = str(amount_str).strip()
        
        # Remove VNĐ, đ, and other currency symbols
        amount_str = re.sub(r'[VNĐđdD\s]', '', amount_str, flags=re.IGNORECASE)
        
        # Remove all non-digit characters except comma and dot
        amount_str = re.sub(r'[^\d,\.]', '', amount_str)
        
        if not amount_str:
            return 0.0
        
        # Count digits only
        digits_only = re.sub(r'[^\d]', '', amount_str)
        
        # Safety check: if the number is too long (more than 10 digits), it might be concatenated
        if len(digits_only) > 10:
            # If it looks like multiple numbers concatenated (e.g., 63325506668391)
            # Try to find patterns that look like separate amounts
            # Common pattern: numbers separated by dots/commas might be separate amounts
            if '.' in amount_str or ',' in amount_str:
                # Split by separator and take the last reasonable part
                parts = re.split(r'[,\.]', amount_str)
                # Find the last part that looks like an amount (4-8 digits)
                for part in reversed(parts):
                    part_digits = re.sub(r'[^\d]', '', part)
                    if 4 <= len(part_digits) <= 8:
                        amount_str = part
                        digits_only = part_digits
                        logger.warning(f"⚠️ Multiple numbers detected, using last reasonable part: {amount_str}")
                        break
                else:
                    # If no reasonable part found, take last 8 digits
                    logger.warning(f"⚠️ Suspiciously long number detected: {amount_str}, taking last 8 digits")
                    digits_only = digits_only[-8:]
                    amount_str = digits_only
            else:
                # No separators, likely concatenated - take last 8 digits
                logger.warning(f"⚠️ Suspiciously long number detected: {amount_str}, taking last 8 digits")
                digits_only = digits_only[-8:]
                amount_str = digits_only
        
        # Handle Vietnamese thousand separators: 68.391 or 68,391
        # Vietnamese typically uses dot or comma as thousand separator
        
        # Case 1: Both dot and comma present
        if '.' in amount_str and ',' in amount_str:
            # Usually: dot is thousand, comma is decimal (68.391,50)
            # Or: comma is thousand, dot is decimal (68,391.50)
            dot_count = amount_str.count('.')
            comma_count = amount_str.count(',')
            
            if dot_count == 1 and comma_count == 1:
                # One of each - determine which is decimal
                dot_pos = amount_str.find('.')
                comma_pos = amount_str.find(',')
                if dot_pos < comma_pos:
                    # Format: 68.391,50 -> dot is thousand, comma is decimal
                    amount_str = amount_str.replace('.', '').replace(',', '.')
                else:
                    # Format: 68,391.50 -> comma is thousand, dot is decimal
                    amount_str = amount_str.replace(',', '')
            else:
                # Multiple separators - check if last part is decimal (1-2 digits)
                parts = re.split(r'[,\.]', amount_str)
                if len(parts) > 1 and len(parts[-1]) <= 2:
                    # Last part is decimal
                    amount_str = ''.join(parts[:-1]) + '.' + parts[-1]
                else:
                    # All are thousand separators - remove all
                    amount_str = amount_str.replace('.', '').replace(',', '')
        
        # Case 2: Only dots
        elif '.' in amount_str:
            parts = amount_str.split('.')
            if len(parts) == 2:
                if len(parts[1]) <= 2:
                    # Decimal: 68.50 -> keep as is
                    pass
                elif len(parts[1]) == 3:
                    # Thousand separator: 68.391 -> 68391 (Vietnamese format)
                    amount_str = amount_str.replace('.', '')
                else:
                    # More than 3 digits - likely thousand separator
                    amount_str = amount_str.replace('.', '')
            else:
                # Multiple dots - check if last part is decimal
                if len(parts[-1]) <= 2:
                    # Last part is decimal
                    amount_str = ''.join(parts[:-1]) + '.' + parts[-1]
                else:
                    # All are thousand separators
                    amount_str = amount_str.replace('.', '')
        
        # Case 3: Only commas
        elif ',' in amount_str:
            parts = amount_str.split(',')
            if len(parts) == 2:
                if len(parts[1]) == 3:
                    # Thousand separator: 68,391 -> 68391 (Vietnamese format - most common)
                    amount_str = amount_str.replace(',', '')
                elif len(parts[1]) <= 2:
                    # Decimal: 68,50 -> 68.50 (less common in Vietnamese invoices)
                    amount_str = amount_str.replace(',', '.')
                else:
                    # More than 3 digits - likely thousand separator
                    amount_str = amount_str.replace(',', '')
            elif len(parts) > 2:
                # Multiple commas - Vietnamese format uses comma as thousand separator
                # Example: 1,234,567 -> 1234567
                # Check if last part is decimal (1-2 digits)
                if len(parts[-1]) <= 2:
                    # Last part is decimal
                    amount_str = ''.join(parts[:-1]) + '.' + parts[-1]
                else:
                    # All are thousand separators (Vietnamese format)
                    amount_str = amount_str.replace(',', '')
            else:
                # Single comma - treat as thousand separator
                amount_str = amount_str.replace(',', '')
        
        try:
            result = float(amount_str)
            return result if result > 0 else 0.0
        except (ValueError, TypeError):
            return 0.0
    
    def _extract_subtotal(self, texts):
        """Extract subtotal amount from Vietnamese invoice"""
        if not texts:
            return 0.0
        
        full_text = texts[0] if texts else ""
        combined_text = " ".join(texts)
        
        # Vietnamese keywords for subtotal
        patterns = [
            r'(?:tổng\s*tiền\s*hàng|tiền\s*hàng|subtotal|tổng\s*trước\s*thuế)[\s:]*([0-9\s,\.]+)',
            r'(?:tổng\s*tiền|tiền\s*hàng)[\s:]*([0-9\s,\.]+)',
        ]
        
        # Search line by line for better accuracy
        text_lines = full_text.split('\n') if full_text else []
        for line in text_lines:
            line_lower = line.lower()
            if 'tổng tiền hàng' in line_lower or 'tiền hàng' in line_lower:
                numbers = re.findall(r'([\d\s,\.]+)', line)
                for num_str in numbers:
                    amount = self._normalize_amount(num_str)
                    if amount > 1000:
                        return amount
        
        for pattern in patterns:
            matches = re.findall(pattern, combined_text, re.IGNORECASE)
            for match in matches:
                amount = self._normalize_amount(match)
                if amount > 1000:
                    return amount
        
        return 0.0
    
    def _extract_vat(self, texts):
        """Extract VAT amount from Vietnamese invoice"""
        if not texts:
            return 0.0
        
        full_text = texts[0] if texts else ""
        combined_text = " ".join(texts)
        
        # Vietnamese keywords for VAT
        patterns = [
            r'(?:VAT|thuế\s*GTGT|thuế\s*VAT|thuế)[\s:]*([0-9\s,\.]+)',
            r'(?:VAT|thuế)[\s:]*([0-9\s,\.]+)',
        ]
        
        # Search line by line for better accuracy
        text_lines = full_text.split('\n') if full_text else []
        for line in text_lines:
            line_lower = line.lower()
            if 'vat' in line_lower or 'thuế' in line_lower:
                # Look for number on same line
                numbers = re.findall(r'([\d\s,\.]+)', line)
                for num_str in numbers:
                    amount = self._normalize_amount(num_str)
                    if 0 < amount < 1000000:  # Reasonable VAT amount
                        return amount
        
        for pattern in patterns:
            matches = re.findall(pattern, combined_text, re.IGNORECASE)
            for match in matches:
                amount = self._normalize_amount(match)
                if amount > 0:
                    return amount
        
        return 0.0
    
    def _extract_total(self, texts):
        """Extract total amount from Vietnamese invoice"""
        if not texts:
            return 0.0
        
        full_text = texts[0] if texts else ""
        combined_text = " ".join(texts)
        
        # Vietnamese keywords: Tổng cộng, Cộng tiền, Thành tiền, Tổng
        # Try multiple patterns with different formats
        patterns = [
            # Pattern: "Tổng Cộng: 68,391" or "Tổng Cộng 68.391"
            r'(?:tổng\s*cộng|cộng\s*tiền|thành\s*tiền|tổng|total|grand\s*total)[\s:]*([0-9\s,\.]+)',
            # Pattern with VNĐ: "Tổng Cộng: 68,391 VNĐ"
            r'(?:tổng\s*cộng|cộng\s*tiền)[\s:]*([0-9\s,\.]+)\s*(?:VNĐ|đ|dong)?',
            # More flexible: any number after "Tổng Cộng"
            r'tổng\s*cộng[^\d]*([\d\s,\.]+)',
        ]
        
        # Find all matches
        all_matches = []
        for pattern in patterns:
            matches = re.findall(pattern, combined_text, re.IGNORECASE)
            all_matches.extend(matches)
        
        # Also search line by line for better accuracy
        text_lines = full_text.split('\n') if full_text else []
        for line in text_lines:
            line_lower = line.lower()
            if 'tổng cộng' in line_lower or 'tổng' in line_lower:
                # Extract numbers from this line
                numbers = re.findall(r'([\d\s,\.]+)', line)
                all_matches.extend(numbers)
        
        # Process matches and return the largest reasonable amount
        amounts = []
        for match in all_matches:
            amount = self._normalize_amount(match)
            if amount > 1000:  # Reasonable minimum for Vietnamese invoices
                amounts.append(amount)
        
        if amounts:
            # Return the largest amount (usually the grand total)
            # But also check if it's reasonable (not too large)
            max_amount = max(amounts)
            # Filter out unreasonably large amounts (likely parsing errors)
            reasonable_amounts = [a for a in amounts if a < 1000000000]  # Less than 1 billion
            if reasonable_amounts:
                return max(reasonable_amounts)
            return max_amount
        
        # Fallback: look for the largest number in the text (might be total)
        # This is less accurate but better than returning 0
        all_numbers = re.findall(r'([\d\s,\.]{4,})', combined_text)
        fallback_amounts = []
        for num_str in all_numbers:
            amount = self._normalize_amount(num_str)
            if 10000 <= amount <= 10000000:  # Reasonable range for Vietnamese invoices
                fallback_amounts.append(amount)
        
        if fallback_amounts:
            return max(fallback_amounts)
        
        return 0.0
    
    def _extract_seller(self, texts):
        """Extract seller/store name from Vietnamese invoice"""
        if not texts:
            return None
        
        full_text = texts[0] if texts else ""
        text_lines = full_text.split('\n') if full_text else []
        
        # Look for business name in first few lines
        for i, line in enumerate(text_lines[:15]):
            line = line.strip()
            
            # Skip empty lines, dates, phone numbers, addresses
            if (len(line) > 2 and 
                not re.match(r'^\d+', line) and  # Not starting with number
                not re.match(r'^\d{1,2}[/\-\.]\d{1,2}', line) and  # Not a date
                not re.match(r'^\+?\d{8,}', line) and  # Not phone number
                not re.search(r'(phiếu|hóa đơn|biên lai|receipt|date|ngày|địa chỉ|address|phone|điện thoại)', line, re.IGNORECASE) and
                not re.search(r'(tổng|total|cộng|tiền|VAT|thuế)', line, re.IGNORECASE) and
                not re.search(r'^[A-Z]{2}\d+', line)):  # Not invoice number
                # Likely business name
                return line
        
        return None
    
    def _extract_phone(self, texts):
        """Extract phone number from invoice"""
        if not texts:
            return None
        
        combined_text = " ".join(texts)
        
        # Vietnamese phone patterns
        patterns = [
            r'\+?84[\s\-]?(\d{9,10})',  # +84 or 84 prefix
            r'0(\d{9,10})',  # 0 prefix
            r'(\d{10,11})',  # 10-11 digits
        ]
        
        for pattern in patterns:
            match = re.search(pattern, combined_text)
            if match:
                phone = match.group(0).strip()
                # Clean up phone number
                phone = re.sub(r'[\s\-]', '', phone)
                return phone
        
        return None
    
    def _extract_address(self, texts):
        """Extract address from invoice"""
        if not texts:
            return None
        
        full_text = texts[0] if texts else ""
        text_lines = full_text.split('\n') if full_text else []
        
        # Look for address patterns (usually contains numbers and street names)
        address_keywords = ['địa chỉ', 'address', 'đường', 'phố', 'street', 'ward', 'phường', 'district', 'quận', 'huyện']
        
        for i, line in enumerate(text_lines[:20]):
            line = line.strip()
            # Check if line contains address keywords or looks like an address
            if (len(line) > 10 and 
                (any(keyword in line.lower() for keyword in address_keywords) or
                 (re.search(r'\d+', line) and re.search(r'[A-Za-zÀ-ỹ]', line)))):
                # Clean up address
                address = re.sub(r'^(địa chỉ|address)[:\-]?\s*', '', line, flags=re.IGNORECASE)
                return address.strip()
        
        return None
    
    def _extract_items(self, texts):
        """Extract items list from invoice"""
        if not texts:
            return []
        
        full_text = texts[0] if texts else ""
        text_lines = full_text.split('\n') if full_text else []
        
        items = []
        in_items_section = False
        
        # Patterns to identify item lines
        item_patterns = [
            r'^\d+\.?\s+',  # Starts with number
            r'\d+\s+x\s+',  # Contains "x" (quantity)
            r'\d+[\s,\.]+\d+\s*$',  # Ends with amount
        ]
        
        for line in text_lines:
            line = line.strip()
            if not line:
                continue
            
            # Skip headers and totals
            if re.search(r'(tổng|total|cộng|tiền|VAT|thuế|phiếu|hóa đơn|bill|receipt)', line, re.IGNORECASE):
                if in_items_section:
                    break  # End of items section
                continue
            
            # Check if this looks like an item line
            is_item = False
            for pattern in item_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    is_item = True
                    break
            
            # Also check for common item patterns: name + quantity + price
            if not is_item and len(line) > 5:
                # Check if line has numbers (likely price/quantity)
                if re.search(r'\d+', line):
                    # Check if it's not a date or phone
                    if not re.match(r'^\d{1,2}[/\-\.]\d{1,2}', line) and not re.match(r'^\+?\d{8,}', line):
                        is_item = True
            
            if is_item:
                in_items_section = True
                item = self._parse_item_line(line)
                if item:
                    items.append(item)
        
        return items
    
    def _parse_item_line(self, line):
        """Parse a single item line into structured data - use structured method"""
        return self._parse_item_line_structured(line)
