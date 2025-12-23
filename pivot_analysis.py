"""pivot_analysis.py - Tạo các pivot table cho phân tích"""
import pandas as pd
import os


class PivotAnalyzer:
    def __init__(self, df):
        self.df = df
        self.pivot_tables = {}

    def create_all_pivots(self):
        """Tạo tất cả các pivot table"""
        print("Đang tạo pivot tables...")

        # 1. Pivot theo sản phẩm và kênh
        if 'Product_Name' in self.df.columns and 'Order_Channel' in self.df.columns and 'Revenue' in self.df.columns:
            pivot1 = self.df.pivot_table(
                index='Product_Name',
                columns='Order_Channel',
                values=['Revenue', 'Quantity'],
                aggfunc={'Revenue': 'sum', 'Quantity': 'sum'},
                fill_value=0
            )

            # Làm phẳng multi-index
            pivot1.columns = [f'{col[1]}_{col[0]}' for col in pivot1.columns]
            pivot1 = pivot1.reset_index()

            # Tính tổng
            pivot1['Total_Revenue'] = pivot1.filter(like='Revenue').sum(axis=1)
            pivot1['Total_Quantity'] = pivot1.filter(like='Quantity').sum(axis=1)
            pivot1 = pivot1.sort_values('Total_Revenue', ascending=False)

            self.pivot_tables['product_channel'] = pivot1
            print("Đã tạo pivot: Sản phẩm theo kênh")

        # 2. Pivot theo thời gian
        if 'Year_Month' in self.df.columns and 'Revenue' in self.df.columns:
            pivot2 = self.df.pivot_table(
                index='Year_Month',
                values=['Revenue', 'Quantity'],
                aggfunc={'Revenue': 'sum', 'Quantity': 'sum'},
                fill_value=0
            ).reset_index()

            pivot2 = pivot2.sort_values('Year_Month')
            self.pivot_tables['monthly_trend'] = pivot2
            print("Đã tạo pivot: Xu hướng theo tháng")

        # 3. Pivot theo nhân viên
        if 'Staff_id' in self.df.columns and 'Revenue' in self.df.columns:
            pivot3 = self.df.pivot_table(
                index='Staff_id',
                values=['Revenue', 'Quantity'],
                aggfunc={'Revenue': 'sum', 'Quantity': 'sum'},
                fill_value=0
            ).reset_index()

            pivot3 = pivot3.sort_values('Revenue', ascending=False)
            pivot3['Rank'] = range(1, len(pivot3) + 1)
            self.pivot_tables['staff_performance'] = pivot3
            print("Đã tạo pivot: Hiệu suất nhân viên")

        # 4. Pivot theo kích cỡ sản phẩm
        if 'Product_Name' in self.df.columns and 'Size' in self.df.columns:
            pivot4 = self.df.pivot_table(
                index='Product_Name',
                columns='Size',
                values=['Quantity', 'Revenue'],
                aggfunc={'Quantity': 'sum', 'Revenue': 'sum'},
                fill_value=0
            )

            # Làm phẳng columns
            pivot4.columns = [f'{col[1]}_{col[0]}' for col in pivot4.columns]
            pivot4 = pivot4.reset_index()

            # Thêm tổng
            size_cols = ['L', 'M', 'S']
            for col in size_cols:
                if f'{col}_Quantity' not in pivot4.columns:
                    pivot4[f'{col}_Quantity'] = 0
                if f'{col}_Revenue' not in pivot4.columns:
                    pivot4[f'{col}_Revenue'] = 0

            pivot4['Total_Quantity'] = pivot4[[f'{c}_Quantity' for c in size_cols]].sum(axis=1)
            pivot4['Total_Revenue'] = pivot4[[f'{c}_Revenue' for c in size_cols]].sum(axis=1)
            pivot4 = pivot4.sort_values('Total_Revenue', ascending=False)

            self.pivot_tables['product_size'] = pivot4
            print("Dã tạo pivot: Sản phẩm theo kích cỡ")

        # 5. Pivot theo sản phẩm và size
        if all(col in self.df.columns for col in ['Product_Name', 'Size', 'Revenue']):
            pivot5 = self.df.pivot_table(
                index=['Product_Name', 'Size'],
                values=['Revenue', 'Quantity'],
                aggfunc={'Revenue': 'sum', 'Quantity': 'sum'},
                fill_value=0
            ).reset_index()

            pivot5 = pivot5.sort_values(['Product_Name', 'Revenue'], ascending=[True, False])
            self.pivot_tables['product_size_detail'] = pivot5
            print("Đã tạo pivot: Chi tiết sản phẩm theo size")

        print(f"Đã tạo tổng cộng {len(self.pivot_tables)} pivot tables")
        return self.pivot_tables

    def save_to_excel(self, output_path='output/pivot_tables.xlsx'):
        """Lưu tất cả pivot tables vào file Excel"""
        if not self.pivot_tables:
            print(" Không có pivot tables để lưu!")
            return False

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            for sheet_name, pivot_df in self.pivot_tables.items():
                # Giới hạn tên sheet (tối đa 31 ký tự)
                sheet_name_short = sheet_name[:31]
                pivot_df.to_excel(writer, sheet_name=sheet_name_short, index=False)

            # Tạo sheet tổng hợp
            summary_data = {
                'Pivot Table': list(self.pivot_tables.keys()),
                'Số dòng': [len(df) for df in self.pivot_tables.values()],
                'Số cột': [len(df.columns) for df in self.pivot_tables.values()]
            }
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Summary', index=False)

        print(f"Đã lưu {len(self.pivot_tables)} pivot tables vào: {output_path}")
        return True

    def save_to_csv(self, output_folder='output/pivot_csv'):
        """Lưu từng pivot table ra file CSV riêng"""
        if not self.pivot_tables:
            print("Không có pivot tables để lưu!")
            return False

        os.makedirs(output_folder, exist_ok=True)

        for sheet_name, pivot_df in self.pivot_tables.items():
            csv_path = f'{output_folder}/{sheet_name}.csv'
            pivot_df.to_csv(csv_path, index=False, encoding='utf-8-sig')
            print(f"Đã lưu: {csv_path}")

        print(f"Đã lưu {len(self.pivot_tables)} file CSV vào thư mục: {output_folder}")
        return True


# Hàm chính cho module nà
def main_pivot_analysis(df_path='output/cleaned_data.csv'):
    """Hàm chính cho phân tích pivot"""
    print("=" * 60)
    print("PHÂN TÍCH PIVOT TABLES")
    print("=" * 60)

    if not os.path.exists(df_path):
        print(f"File {df_path} không tồn tại!")
        return None

    # Đọc dữ liệu đã làm sạch
    df = pd.read_csv(df_path)
    print(f" Đã tải {len(df)} bản ghi từ {df_path}")

    # Khởi tạo analyzer
    analyzer = PivotAnalyzer(df)

    # Tạo pivot tables
    pivots = analyzer.create_all_pivots()

    # Lưu ra Excel
    analyzer.save_to_excel()

    # Lưu ra CSV
    analyzer.save_to_csv()

    return pivots


if __name__ == "__main__":
    main_pivot_analysis()