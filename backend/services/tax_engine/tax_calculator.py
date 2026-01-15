import yaml
from pathlib import Path

class TaxEngine:
    def __init__(self, config_path=None):
        if config_path is None:
            config_path = Path(__file__).parent.parent.parent / "configs" / "tax_rules.yaml"
        self.rules = self._load_rules(config_path)
    
    def _load_rules(self, config_path):
        default_rules = {
            "food_service": {
                "vat_rate": 0.025,
                "pit_rate": 0.015,
                "license_fee": 1000000,
                "threshold": 100000000
            },
            "retail": {
                "vat_rate": 0.02,
                "pit_rate": 0.01,
                "license_fee": 1000000,
                "threshold": 100000000
            }
        }
        
        try:
            if Path(config_path).exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f)
        except:
            pass
        
        return default_rules
    
    def calculate_tax(self, revenue, expenses, business_type="food_service"):
        rules = self.rules.get(business_type, self.rules["food_service"])
        
        vat = revenue * rules["vat_rate"]
        pit = revenue * rules["pit_rate"]
        license_fee = rules["license_fee"]
        
        total_tax = vat + pit + license_fee
        
        notes = []
        if revenue > rules["threshold"]:
            notes.append(f"Doanh thu vượt ngưỡng {rules['threshold']:,.0f} VNĐ")
            notes.append("Cần đăng ký hóa đơn điện tử")
        
        return {
            "estimated_revenue": revenue,
            "estimated_expenses": expenses,
            "estimated_tax": {
                "vat": vat,
                "pit": pit,
                "license_fee": license_fee,
                "total": total_tax
            },
            "notes": notes,
            "disclaimer": "Kết quả mang tính tham khảo, phụ thuộc quyết định cơ quan thuế"
        }
