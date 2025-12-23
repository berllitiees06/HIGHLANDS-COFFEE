"""data_preprocess.py - Xử lý và chuẩn hóa dữ liệu"""
import pandas as pd
import numpy as np
import os
from datetime import datetime
class DataPreprocessor:
    def __init__(self, data_path):
        self.data_path = data_path
        self.df = None

    def load_data(self):
        """Tải dữ liệu từ file CSV"""
        try:
            # Đọc file CSV với encoding UTF-8
            self.df = pd.read_csv(self.data_path, sep=';', encoding='utf-8')
            print(f" Đã tải {len(self.df)} bản ghi từ {self.data_path}")
            return True
        except Exception as e:
            print(f" Lỗi khi tải dữ liệu: {e}")
            return False

    def clean_data(self):
        """Làm sạch và chuẩn hóa dữ liệu"""
        if self.df is None:
            print(" Không có dữ liệu để làm sạch!")
            return False

        # 1. Chuẩn hóa tên cột
        self.df.columns = self.df.columns.str.strip()

        column_mapping = {
            'Oder_chanel': 'Order_Channel',
            'Product Name ': 'Product_Name',
            'Product Name': 'Product_Name',
            'Applied Price': 'Applied_Price',
            'Actual Selling Price': 'Actual_Selling_Price',
            'Discount Online (%)': 'Discount_Online',
            'Original Price Online': 'Original_Price_Online',
            'Original Price Offline': 'Original_Price_Offline'
        }

        for old_name, new_name in column_mapping.items():
            if old_name in self.df.columns:
                self.df.rename(columns={old_name: new_name}, inplace=True)

        # 2. Chuẩn hóa ngày tháng
        if 'Date' in self.df.columns:
            self.df['Date'] = pd.to_datetime(self.df['Date'], format='%d/%m/%Y', errors='coerce')

            # Thêm các cột thời gian
            self.df['Year'] = self.df['Date'].dt.year
            self.df['Month'] = self.df['Date'].dt.month
            self.df['Quarter'] = self.df['Date'].dt.quarter
            self.df['Day'] = self.df['Date'].dt.day
            self.df['Year_Month'] = self.df['Date'].dt.strftime('%Y-%m')
            self.df['Year_Quarter'] = self.df['Year'].astype(str) + '-Q' + self.df['Quarter'].astype(str)

        # 3. Chuẩn hóa dữ liệu số
        numeric_cols = ['Quantity', 'Original_Price_Online', 'Original_Price_Offline',
                        'Discount_Online', 'Applied_Price', 'Actual_Selling_Price', 'Revenue']

        for col in numeric_cols:
            if col in self.df.columns:
                self.df[col] = pd.to_numeric(self.df[col], errors='coerce')

        # 4. Chuẩn hóa dữ liệu chuỗi
        if 'Product_Name' in self.df.columns:
            self.df['Product_Name'] = self.df['Product_Name'].str.strip()

        if 'Order_Channel' in self.df.columns:
            self.df['Order_Channel'] = self.df['Order_Channel'].str.strip().str.title()

        if 'Size' in self.df.columns:
            self.df['Size'] = self.df['Size'].str.strip().str.upper()

        if 'Staff_id' in self.df.columns:
            self.df['Staff_id'] = self.df['Staff_id'].str.strip()

        # 5. Xử lý dữ liệu thiếu
        print("Thống kê dữ liệu thiếu:")
        missing_data = self.df.isnull().sum()
        missing_cols = missing_data[missing_data > 0]

        if len(missing_cols) > 0:
            print(missing_cols)

            # Điền giá trị thiếu cho Revenue
            if 'Revenue' in self.df.columns and 'Quantity' in self.df.columns and 'Actual_Selling_Price' in self.df.columns:
                missing_revenue = self.df['Revenue'].isnull()
                if missing_revenue.any():
                    self.df.loc[missing_revenue, 'Revenue'] = (
                            self.df.loc[missing_revenue, 'Quantity'] *
                            self.df.loc[missing_revenue, 'Actual_Selling_Price']
                    )

        # 6. Xóa dòng không có thông tin quan trọng
        important_cols = ['Product_Name', 'Quantity', 'Actual_Selling_Price', 'Revenue']
        important_cols = [col for col in important_cols if col in self.df.columns]

        if important_cols:
            self.df = self.df.dropna(subset=important_cols)

        print(f" Đã làm sạch dữ liệu. Còn {len(self.df)} bản ghi hợp lệ.")
        return True

    def get_summary(self):
        """Tạo báo cáo tổng quan dữ liệu"""
        if self.df is None:
            return None

        summary = {
            'total_records': len(self.df),
            'start_date': self.df['Date'].min() if 'Date' in self.df.columns else None,
            'end_date': self.df['Date'].max() if 'Date' in self.df.columns else None,
            'total_products': self.df['Product_Name'].nunique() if 'Product_Name' in self.df.columns else 0,
            'total_channels': self.df['Order_Channel'].nunique() if 'Order_Channel' in self.df.columns else 0,
            'total_staff': self.df['Staff_id'].nunique() if 'Staff_id' in self.df.columns else 0,
            'total_revenue': self.df['Revenue'].sum() if 'Revenue' in self.df.columns else 0,
            'total_quantity': self.df['Quantity'].sum() if 'Quantity' in self.df.columns else 0
        }

        return summary

    def save_cleaned_data(self, output_path='output/cleaned_data.csv'):
        """Lưu dữ liệu đã làm sạch"""
        if self.df is not None:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            self.df.to_csv(output_path, index=False, encoding='utf-8-sig')
            print(f"Đã lưu dữ liệu đã làm sạch tại: {output_path}")
            return True
        return False

    def generate_test_data(self, num_records=1000, output_path='data/highlands_test.csv'):
        """Tạo dữ liệu test mở rộng"""
        if self.df is None:
            print(" Không có dữ liệu mẫu để tạo test data!")
            return False

        # Lấy thông tin từ dữ liệu gốc
        products = self.df['Product_Name'].unique() if 'Product_Name' in self.df.columns else ['Cappuccino', 'Latte',
                                                                                               'Mocha']
        sizes = ['S', 'M', 'L']
        channels = ['Online', 'Offline']
        staff_ids = [f'NV{i:02d}' for i in range(1, 51)]

        # Tạo dữ liệu ngẫu nhiên
        np.random.seed(42)

        test_data = {
            'Sale_id': [f'S{1000 + i:04d}' for i in range(num_records)],
            'Date': pd.date_range(start='2023-01-01', periods=num_records, freq='D').strftime('%d/%m/%Y'),
            'Product_Name': np.random.choice(products, num_records),
            'Size': np.random.choice(sizes, num_records),
            'Quantity': np.random.randint(1, 10, num_records),
            'Original_Price_Online': np.random.choice([35000, 45000, 55000, 65000, 75000], num_records),
            'Original_Price_Offline': np.random.choice([29000, 39000, 49000, 59000, 69000], num_records),
            'Discount_Online': np.random.randint(5, 20, num_records),
            'Applied_Price': np.random.choice([35000, 45000, 55000, 65000], num_records),
            'Order_Channel': np.random.choice(channels, num_records),
            'Actual_Selling_Price': np.random.choice([35000, 45000, 55000, 65000], num_records),
            'Staff_id': np.random.choice(staff_ids, num_records)
        }

        # Tính Revenue
        test_data['Revenue'] = test_data['Quantity'] * test_data['Actual_Selling_Price']

        # Tạo DataFrame
        test_df = pd.DataFrame(test_data)

        # Lưu file
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        test_df.to_csv(output_path, sep=';', index=False, encoding='utf-8-sig')
        print(f" Đã tạo {num_records} bản ghi test tại: {output_path}")

        return True

data_path = 'data/data_1.csv'
# Hàm chính cho module này
def main_preprocess():
    """Hàm chính cho tiền xử lý dữ liệu"""
    print("=" * 60)
    print("TIỀN XỬ LÝ DỮ LIỆU HIGHLANDS")
    print("=" * 60)

    # Đường dẫn dữ liệu
    data_path = 'data/data_1.csv'

    if not os.path.exists(data_path):
        print(f" File {data_path} không tồn tại!")
        return None

    # Khởi tạo preprocessor
    preprocessor = DataPreprocessor(data_path)

    # 1. Tải dữ liệu
    if not preprocessor.load_data():
        return None

    # 2. Làm sạch dữ liệu
    if not preprocessor.clean_data():
        return None

    # 3. Tạo báo cáo tổng quan
    summary = preprocessor.get_summary()
    if summary:
        print(" BÁO CÁO TỔNG QUAN DỮ LIỆU:")
        for key, value in summary.items():
            if 'revenue' in key or 'quantity' in key:
                print(f"  {key.replace('_', ' ').title()}: {value:,.0f}")
            elif 'date' in key and value:
                print(f"  {key.replace('_', ' ').title()}: {value.strftime('%d/%m/%Y')}")
            else:
                print(f"  {key.replace('_', ' ').title()}: {value}")

    # 4. Lưu dữ liệu đã làm sạch
    preprocessor.save_cleaned_data()

    # 5. Tạo dữ liệu test (tùy chọn)
    create_test = input(" Bạn có muốn tạo dữ liệu test mở rộng? (y/n): ")
    if create_test.lower() == 'y':
        num_records = int(input("Nhập số bản ghi muốn tạo (mặc định 1000): ") or 1000)
        preprocessor.generate_test_data(num_records)

    return preprocessor.df


if __name__ == "__main__":
    df = main_preprocess()