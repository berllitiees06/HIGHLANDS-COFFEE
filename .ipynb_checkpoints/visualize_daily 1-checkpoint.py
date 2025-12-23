"""visualize_daily.py - Biểu đồ doanh thu theo ngày/tháng"""
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from datetime import datetime


class DailyVisualizer:
    def __init__(self, df):
        self.df = df
        self.output_dir = 'output/charts'
        os.makedirs(self.output_dir, exist_ok=True)

    def plot_daily_revenue(self, figsize=(14, 6)):
        """Biểu đồ doanh thu theo ngày"""
        if 'Date' not in self.df.columns or 'Revenue' not in self.df.columns:
            print("Thiếu cột Date hoặc Revenue!")
            return False

        # Chuẩn bị dữ liệu
        daily_data = self.df.groupby('Date')['Revenue'].sum().reset_index()
        daily_data = daily_data.sort_values('Date')

        # Tạo biểu đồ
        plt.figure(figsize=figsize)

        # Line chart
        plt.subplot(1, 2, 1)
        plt.plot(daily_data['Date'], daily_data['Revenue'] / 1e6,
                 color='#2E86AB', linewidth=2, marker='o', markersize=4)
        plt.xlabel('Ngày', fontsize=12)
        plt.ylabel('Doanh thu (triệu VND)', fontsize=12)
        plt.title('Doanh thu theo ngày', fontsize=14, fontweight='bold')
        plt.grid(True, alpha=0.3)
        plt.xticks(rotation=45)

        # Bar chart (top 10 ngày cao nhất)
        plt.subplot(1, 2, 2)
        top_days = daily_data.nlargest(10, 'Revenue')
        plt.barh(top_days['Date'].dt.strftime('%d/%m/%Y'),
                 top_days['Revenue'] / 1e6,
                 color='#A23B72')
        plt.xlabel('Doanh thu (triệu VND)', fontsize=12)
        plt.title('Top 10 ngày doanh thu cao nhất', fontsize=14, fontweight='bold')
        plt.gca().invert_yaxis()

        # Thêm giá trị trên cột
        for i, (date_str, revenue) in enumerate(zip(top_days['Date'].dt.strftime('%d/%m/%Y'),
                                                    top_days['Revenue'] / 1e6)):
            plt.text(revenue + 0.1, i, f'{revenue:.1f}', va='center', fontsize=10)

        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/daily_revenue.png', dpi=300, bbox_inches='tight')
        plt.close()

        print(f"Đã lưu biểu đồ doanh thu theo ngày: {self.output_dir}/daily_revenue.png")
        return True

    def plot_monthly_trend(self, figsize=(12, 6)):
        """Biểu đồ xu hướng theo tháng"""
        if 'Year_Month' not in self.df.columns or 'Revenue' not in self.df.columns:
            print("Thiếu cột Year_Month hoặc Revenue!")
            return False

        # Chuẩn bị dữ liệu
        monthly_data = self.df.groupby('Year_Month').agg({
            'Revenue': 'sum',
            'Quantity': 'sum'
        }).reset_index()

        monthly_data = monthly_data.sort_values('Year_Month')

        # Tạo biểu đồ
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=figsize)

        # Biểu đồ doanh thu
        bars1 = ax1.bar(range(len(monthly_data)), monthly_data['Revenue'] / 1e6,
                        color='#4ECDC4')
        ax1.set_xlabel('Tháng', fontsize=12)
        ax1.set_ylabel('Doanh thu (triệu VND)', fontsize=12)
        ax1.set_title('Doanh thu theo tháng', fontsize=14, fontweight='bold')
        ax1.set_xticks(range(len(monthly_data)))
        ax1.set_xticklabels(monthly_data['Year_Month'], rotation=45)
        ax1.grid(True, alpha=0.3, axis='y')

        # Thêm giá trị trên cột
        for bar, revenue in zip(bars1, monthly_data['Revenue'] / 1e6):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width() / 2., height,
                     f'{revenue:.0f}', ha='center', va='bottom', fontsize=9)

        # Biểu đồ số lượng
        bars2 = ax2.bar(range(len(monthly_data)), monthly_data['Quantity'],
                        color='#FF6B6B')
        ax2.set_xlabel('Tháng', fontsize=12)
        ax2.set_ylabel('Số lượng sản phẩm', fontsize=12)
        ax2.set_title('Số lượng sản phẩm theo tháng', fontsize=14, fontweight='bold')
        ax2.set_xticks(range(len(monthly_data)))
        ax2.set_xticklabels(monthly_data['Year_Month'], rotation=45)
        ax2.grid(True, alpha=0.3, axis='y')

        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/monthly_trend.png', dpi=300, bbox_inches='tight')
        plt.close()

        print(f"Đã lưu biểu đồ xu hướng tháng: {self.output_dir}/monthly_trend.png")
        return True

    def plot_quarterly_comparison(self, figsize=(10, 6)):
        """So sánh doanh thu theo quý"""
        if 'Year_Quarter' not in self.df.columns or 'Revenue' not in self.df.columns:
            print("Thiếu cột Year_Quarter hoặc Revenue!")
            return False

        # Chuẩn bị dữ liệu
        quarterly_data = self.df.groupby('Year_Quarter').agg({
            'Revenue': 'sum',
            'Quantity': 'sum'
        }).reset_index()

        quarterly_data = quarterly_data.sort_values('Year_Quarter')

        # Tạo biểu đồ
        fig, ax1 = plt.subplots(figsize=figsize)

        x = range(len(quarterly_data))
        width = 0.35

        bars1 = ax1.bar([i - width / 2 for i in x], quarterly_data['Revenue'] / 1e6,
                        width, label='Doanh thu (triệu VND)', color='#1A936F')

        ax2 = ax1.twinx()
        bars2 = ax2.bar([i + width / 2 for i in x], quarterly_data['Quantity'],
                        width, label='Số lượng', color='#114B5F', alpha=0.7)

        ax1.set_xlabel('Quý', fontsize=12)
        ax1.set_ylabel('Doanh thu (triệu VND)', fontsize=12, color='#1A936F')
        ax2.set_ylabel('Số lượng sản phẩm', fontsize=12, color='#114B5F')
        ax1.set_title('So sánh doanh thu và số lượng theo quý', fontsize=14, fontweight='bold')
        ax1.set_xticks(x)
        ax1.set_xticklabels(quarterly_data['Year_Quarter'], rotation=0)

        # Kết hợp legend
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')

        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/quarterly_comparison.png', dpi=300, bbox_inches='tight')
        plt.close()

        print(f"Đã lưu biểu đồ so sánh quý: {self.output_dir}/quarterly_comparison.png")
        return True

    def create_all_charts(self):
        """Tạo tất cả biểu đồ liên quan đến thời gian"""
        print(" Đang tạo biểu đồ theo thời gian...")

        results = []
        results.append(self.plot_daily_revenue())
        results.append(self.plot_monthly_trend())
        results.append(self.plot_quarterly_comparison())

        success_count = sum(results)
        print(f"Đã tạo {success_count}/{len(results)} biểu đồ theo thời gian")
        return success_count


# Hàm chính cho module này
def main_visualize_daily(df_path='output/cleaned_data.csv'):
    """Hàm chính cho visualization theo ngày"""
    print("=" * 60)
    print("TRỰC QUAN HÓA DỮ LIỆU THEO THỜI GIAN")
    print("=" * 60)

    if not os.path.exists(df_path):
        print(f" File {df_path} không tồn tại!")
        return False

    # Đọc dữ liệu
    df = pd.read_csv(df_path, parse_dates=['Date'])
    print(f"Đã tải {len(df)} bản ghi")

    # Khởi tạo visualizer
    visualizer = DailyVisualizer(df)

    # Tạo tất cả biểu đồ
    visualizer.create_all_charts()

    return True


if __name__ == "__main__":
    main_visualize_daily()