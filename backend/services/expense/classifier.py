class ExpenseClassifier:
    CATEGORIES = {
        "materials": ["thực phẩm", "nguyên liệu", "hàng hóa", "vật liệu"],
        "rent": ["thuê", "mặt bằng", "nhà"],
        "utilities": ["điện", "nước", "internet", "viễn thông"],
        "labor": ["lương", "công", "nhân viên"],
        "depreciation": ["máy móc", "thiết bị"],
        "other": []
    }
    
    DEDUCTIBLE = ["materials", "rent", "utilities", "labor", "depreciation"]
    
    def classify(self, description):
        description_lower = description.lower()
        
        for category, keywords in self.CATEGORIES.items():
            for keyword in keywords:
                if keyword in description_lower:
                    return {
                        "category": category,
                        "is_deductible": category in self.DEDUCTIBLE
                    }
        
        return {
            "category": "other",
            "is_deductible": False
        }
    
    def get_category_name_vi(self, category):
        mapping = {
            "materials": "Nguyên vật liệu",
            "rent": "Thuê mặt bằng",
            "utilities": "Điện nước internet",
            "labor": "Nhân công",
            "depreciation": "Khấu hao",
            "other": "Khác"
        }
        return mapping.get(category, "Khác")
