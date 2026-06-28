from datetime import datetime


BASE_PRODUCTS = [
    ("industrial machinery", "Hydraulic Press Machine", "Rs 2.5 Lakh / Piece", 250000, 250000, "Mahalaxmi Engineering Works", "Ahmedabad, Gujarat", "Ahmedabad", "Gujarat"),
    ("industrial machinery", "CNC Lathe Machine", "Rs 8.75 Lakh / Unit", 875000, 875000, "Precitech Machines Pvt Ltd", "Rajkot, Gujarat", "Rajkot", "Gujarat"),
    ("industrial machinery", "Automatic Packaging Machine", "Rs 4.2 Lakh / Piece", 420000, 420000, "Packwell Systems", "Pune, Maharashtra", "Pune", "Maharashtra"),
    ("industrial machinery", "Industrial Air Compressor", "Rs 95000 / Unit", 95000, 95000, "Airmax Engineers", "Coimbatore, Tamil Nadu", "Coimbatore", "Tamil Nadu"),
    ("industrial machinery", "Food Processing Plant", "Rs 12 Lakh / Set", 1200000, 1200000, "Star Food Equipments", "Noida, Uttar Pradesh", "Noida", "Uttar Pradesh"),
    ("industrial machinery", "Material Handling Conveyor", "Rs 1.8 Lakh / Unit", 180000, 180000, "Conveytech India", "Faridabad, Haryana", "Faridabad", "Haryana"),
    ("electronics", "Industrial Control Panel", "Rs 45000 / Piece", 45000, 45000, "Voltcon Automation", "Delhi, Delhi", "Delhi", "Delhi"),
    ("electronics", "LED Display Module", "Rs 1200 / Piece", 1200, 1200, "Bright Pixel Electronics", "Bengaluru, Karnataka", "Bengaluru", "Karnataka"),
    ("electronics", "Servo Motor Drive", "Rs 18500 / Unit", 18500, 18500, "MotionTech Controls", "Chennai, Tamil Nadu", "Chennai", "Tamil Nadu"),
    ("electronics", "PCB Assembly Service", "Rs 250 / Piece", 250, 250, "CircuitWorks India", "Hyderabad, Telangana", "Hyderabad", "Telangana"),
    ("electronics", "Power Distribution Unit", "Rs 32000 / Unit", 32000, 32000, "ElectroGrid Systems", "Mumbai, Maharashtra", "Mumbai", "Maharashtra"),
    ("electronics", "PLC Automation System", "Rs 1.35 Lakh / Set", 135000, 135000, "Axis Automation", "Vadodara, Gujarat", "Vadodara", "Gujarat"),
    ("textiles", "Cotton Fabric Roll", "Rs 85 / Meter", 85, 85, "Shree Textiles", "Surat, Gujarat", "Surat", "Gujarat"),
    ("textiles", "Power Loom Machine", "Rs 3.6 Lakh / Unit", 360000, 360000, "LoomTech Industries", "Ludhiana, Punjab", "Ludhiana", "Punjab"),
    ("textiles", "Polyester Yarn", "Rs 145 / Kg", 145, 145, "FiberLine Traders", "Surat, Gujarat", "Surat", "Gujarat"),
    ("textiles", "Dyeing Machine", "Rs 5.8 Lakh / Unit", 580000, 580000, "ColorFab Equipments", "Tiruppur, Tamil Nadu", "Tiruppur", "Tamil Nadu"),
    ("textiles", "Industrial Sewing Machine", "Rs 42000 / Piece", 42000, 42000, "StitchPro Machines", "Jaipur, Rajasthan", "Jaipur", "Rajasthan"),
    ("textiles", "Non Woven Fabric", "Rs 120 / Kg", 120, 120, "EcoTex Suppliers", "Kolkata, West Bengal", "Kolkata", "West Bengal"),
]


def demo_records() -> list[dict]:
    scraped_date = datetime.now().strftime("%Y-%m-%d")
    records = []
    for index, item in enumerate(BASE_PRODUCTS, start=1):
        category, name, price, price_min, price_max, supplier, location, city, state = item
        slug = name.lower().replace(" ", "-")
        records.append(
            {
                "category": category,
                "marketplace": "demo_b2b_marketplace",
                "product_name": name,
                "price": price,
                "currency": "INR",
                "price_min": price_min,
                "price_max": price_max,
                "price_min_inr": price_min,
                "price_max_inr": price_max,
                "supplier_name": supplier,
                "location": location,
                "city": city,
                "state": state,
                "product_url": f"https://demo-b2b.local/products/{slug}-{index}",
                "source_url": "demo_seed_data",
                "scraped_date": scraped_date,
            }
        )
    return records

