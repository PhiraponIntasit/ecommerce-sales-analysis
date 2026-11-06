# คู่มือสร้าง Power BI Dashboard (Olist E-commerce)

คู่มือนี้พาสร้างไฟล์ `Olist_Sales_Dashboard.pbix` ทีละขั้น ใช้เวลาประมาณ 2–3 ชั่วโมง
ต้องใช้ **Power BI Desktop** (ฟรี, Windows) — ดาวน์โหลดจาก Microsoft Store

> ก่อนเริ่ม: รัน `python src/prepare_data.py` ให้มีไฟล์ใน `data/processed/` ครบ 7 ไฟล์

---

## ขั้นที่ 1 — นำเข้าข้อมูล (Get Data)

1. **Home → Get data → Text/CSV** แล้วเลือกไฟล์ทีละไฟล์ใน `data/processed/`
   (หรือใช้ **Get data → Folder** แล้ว Combine ทีเดียว ก็ได้แต่จะยุ่งกว่า)
2. ทุกไฟล์ให้กด **Transform Data** (ไม่ใช่ Load) เพื่อเช็ค data type ใน Power Query:

| ตาราง | คอลัมน์ | Type ที่ต้องเป็น |
|---|---|---|
| fact_orders | `order_date` | Date |
| fact_orders | `order_purchase_timestamp` | Date/Time |
| fact_orders | `is_revenue_order`, `is_delivered` | True/False |
| fact_orders | `product_value`, `freight_value`, `payment_value`, `delivery_days` | Decimal number |
| fact_orders | `is_late`, `days_late`, `review_score` | Whole number |
| fact_order_items | `order_date` | Date |
| fact_order_items | `price`, `freight_value`, `line_total` | Decimal number |
| dim_date | `date` | Date |

3. ⚠️ ถ้า Power BI ตั้งค่า Locale เป็นไทย ตัวเลขทศนิยมอาจอ่านผิด → **File → Options → Current File → Regional settings → Locale = English (United States)**
4. กด **Close & Apply**

## ขั้นที่ 2 — สร้าง Data Model (Model view)

ลบ relationship ที่ Power BI สร้างให้อัตโนมัติทั้งหมดก่อน แล้วสร้างใหม่ตามนี้ (ลากคอลัมน์ไปวางทับกัน):

```
dim_date[date]                     1 ──▶ *  fact_orders[order_date]
dim_customer[customer_unique_id]   1 ──▶ *  fact_orders[customer_unique_id]
dim_customer[customer_unique_id]   1 ──▶ 1  customer_rfm[customer_unique_id]
fact_orders[order_id]              1 ──▶ *  fact_order_items[order_id]
dim_product[product_id]            1 ──▶ *  fact_order_items[product_id]
dim_seller[seller_id]              1 ──▶ *  fact_order_items[seller_id]
```

- Cross filter direction: **Single** ทุกเส้น (ทิศทางกรองจาก dim → fact)
- **ไม่ต้อง** เชื่อม `dim_date` กับ `fact_order_items` — วันที่จะกรองผ่าน `fact_orders` ลงมาเอง
- คลิกตาราง `dim_date` → **Table tools → Mark as date table** → เลือกคอลัมน์ `date`
- ตาราง `dim_date`: เลือก `month_name` → **Sort by column = month_num**
- ซ่อน (Hide in report view) คอลัมน์ ID ในตาราง fact ทั้งหมด เพื่อให้ Field list สะอาด

```
            dim_date        dim_customer ── customer_rfm
                 \             /
                  ▼           ▼
                   fact_orders
                        │ (order_id)
                        ▼
  dim_product ──▶ fact_order_items ◀── dim_seller
```

## ขั้นที่ 3 — สร้าง Measures

1. **Home → Enter data** → ตั้งชื่อตาราง `_Measures` → Load (ตารางเปล่า)
2. คลิกขวาที่ `_Measures` → **New measure** แล้ว copy สูตรจาก [`measures.dax`](measures.dax) ทีละอัน
3. ตั้ง Format:
   - `Revenue`, `Avg Order Value`, `Freight` → Currency / ทศนิยม 0–2 ตำแหน่ง
   - ทุกตัวที่ลงท้ายด้วย `%` → Percentage, 1 ตำแหน่ง
   - `Avg Review Score` → Decimal 2 ตำแหน่ง
4. สร้าง Calculated column 2 ตัวท้ายไฟล์ (`Delivery Bucket`, `Weekday Order`) ในตาราง `fact_orders`
   แล้วตั้ง `purchase_weekday` → **Sort by column = Weekday Order**

### ✅ เช็คความถูกต้อง — ใส่ Card แล้วตัวเลขต้องตรงนี้ (ไม่มี filter)

| Measure | ค่าที่ควรได้ |
|---|---|
| Revenue | 13,494,401 (≈ R$13.49M) |
| Orders | 98,199 |
| Customers | 94,983 |
| Avg Order Value | 160.27 |
| Avg Review Score | 4.09 |
| Late Delivery % | 6.8% |
| Repeat Customer % | 3.0% |
| Avg Review (On time) / (Late) | 4.29 / 2.27 |

ถ้าไม่ตรง ส่วนใหญ่เกิดจาก data type ผิด (ขั้นที่ 1) หรือ relationship ผิดทิศ (ขั้นที่ 2)

## ขั้นที่ 4 — ใส่ Theme

**View → Themes → Browse for themes** → เลือก [`olist_theme.json`](olist_theme.json)
(สีหลักน้ำเงิน, สีเน้นส้มสำหรับสิ่งที่เป็นปัญหา, การ์ดขาวมุมโค้งบนพื้นเทาอ่อน)

## ขั้นที่ 5 — ออกแบบ 4 หน้า Dashboard

ขนาดหน้า: **16:9 (1280 × 720)** ทุกหน้า ใช้ layout เดียวกัน:
แถบบน = ชื่อหน้า + Slicer → แถวที่ 2 = KPI cards → ด้านล่าง = กราฟ 2–3 ตัว

### หน้า 1: Executive Overview — "ภาพรวมธุรกิจ"
| ตำแหน่ง | Visual | Field |
|---|---|---|
| บน | Slicer ×3 | `dim_date[year]` (Tile), `dim_customer[customer_region]` (Dropdown), `dim_product[category]` (Dropdown) |
| แถว KPI | Card (new) ×5 | Revenue (+ Revenue YoY % เป็น reference label), Orders, Customers, Avg Order Value, Avg Review Score |
| ซ้ายกลาง (กว้าง) | Line chart | X = `dim_date[year_month]`, Y = Revenue |
| ขวากลาง | Bar chart (แนวนอน) | Y = `dim_product[category]`, X = Revenue, Filter Top N = 10 |
| ล่าง | Filled map / Shape map | Location = `dim_customer[customer_state_name]` + Country = Brazil, Color saturation = Revenue |

> Tip: Filled map ต้องเปิดใน **File → Options → Security → Use Map and Filled Map visuals**
> ถ้า map ไม่ขึ้น ให้ตั้ง Data category ของ `customer_state_name` = **State or Province**

### หน้า 2: Sales & Products — "สินค้าอะไรทำเงิน"
| Visual | Field |
|---|---|
| Line and clustered column chart (Pareto) | X = category, Column = Revenue, Line = Category Cumulative % (sort by Revenue desc) |
| Matrix | Rows = category, Columns = `dim_date[year]`, Values = Revenue, Revenue YoY % (ใส่ conditional formatting icon ↑↓) |
| Scatter chart | Details = category, X = Items Sold, Y = Avg Item Price, Size = Revenue → เห็นกลุ่ม "ขายเยอะราคาถูก" vs "ขายน้อยราคาแพง" |
| Card | Freight % of Revenue, Active Sellers |

### หน้า 3: Delivery & Customer Experience — "การส่งของกระทบรีวิวแค่ไหน" ⭐ หน้าสำคัญที่สุด
| Visual | Field |
|---|---|
| Card ×4 | On-time Delivery %, Avg Delivery Days, Avg Review (On time), Avg Review (Late) |
| Clustered column | X = `Delivery Bucket`, Y = Avg Review Score (ใช้ conditional color: bucket ที่ late = ส้ม) |
| Bar chart | Y = `customer_state`, X = Avg Delivery Days, sort desc |
| Table | state, Orders, Avg Delivery Days, Late Delivery %, Freight % of Revenue, Avg Review Score (ใส่ Data bars / Background color scale) |

### หน้า 4: Customers — "ลูกค้าเป็นใคร กลับมาซื้อไหม"
| Visual | Field |
|---|---|
| Card | Repeat Customer %, Customers |
| Clustered bar | Y = `customer_rfm[segment]`, X = RFM Customer Share % และ RFM Revenue Share % |
| Bar chart | `fact_orders[main_payment_type]` × Orders |
| Matrix (heatmap) | Rows = `purchase_weekday`, Columns = `purchase_hour`, Values = Orders → Conditional formatting → Background color (ขาว → น้ำเงิน) ปิดตัวเลข |

## ขั้นที่ 6 — ขัดเกลาให้ดูมืออาชีพ

- ตั้งชื่อกราฟเป็น **ประโยคบอก insight** ไม่ใช่ชื่อแกน เช่น "Late orders get 2 stars less" แทน "Avg Review by Bucket"
- ใส่ **Text box** สรุป 2–3 บรรทัดในแต่ละหน้า (เอาจาก Findings ใน notebook)
- **Page navigation:** Insert → Buttons → Navigator → Page navigator ใส่แถบบนทุกหน้า
- **Tooltip page:** สร้างหน้าเล็ก (Page size = Tooltip) แสดง Revenue / Orders / Late % แล้วผูกกับ map
- **Sync slicers:** View → Sync slicers ให้ Year/Region ใช้ร่วมกันทุกหน้า
- ปิด gridline ที่ไม่จำเป็น, ใช้สีส้มเฉพาะจุดที่เป็นปัญหา, ทุกอย่างอื่นใช้น้ำเงิน/เทา
- ตรวจ **Performance analyzer** ว่าแต่ละ visual โหลด < 1 วินาที

## ขั้นที่ 7 — Export ไปใส่ Portfolio

1. Save เป็น `powerbi/Olist_Sales_Dashboard.pbix`
2. Capture หน้าจอแต่ละหน้า (หรือ **File → Export → Export to PDF**) แล้วบันทึกที่
   `reports/dashboard/01_overview.png` … `04_customers.png`
3. (แนะนำ) **Publish to web** ผ่าน Power BI Service แล้วเอาลิงก์ใส่ README
   — ถ้าบัญชีมหาวิทยาลัยใช้ Publish to web ไม่ได้ ให้ทำวิดีโอ/GIF สั้นๆ ตอนกด slicer แทน
4. แก้ README หลักในส่วน "Power BI Dashboard" ให้แสดงรูป screenshot

> ไฟล์ `.pbix` ขนาดประมาณ 15–25 MB push ขึ้น GitHub ได้ปกติ (จำกัด 100 MB ต่อไฟล์)
