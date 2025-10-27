"""Generate test Excel file with 30+ sheets for Multi-Sheet Intelligence testing

This script creates a realistic financial report with multiple sheets
containing sales, expenses, transactions, and other marketplace data.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

def generate_sales_data(num_rows=100):
    """Generate sales data"""
    start_date = datetime(2024, 1, 1)
    dates = [start_date + timedelta(days=i) for i in range(num_rows)]
    
    products = ['Product_A', 'Product_B', 'Product_C', 'Product_D', 'Product_E']
    categories = ['Electronics', 'Clothing', 'Food', 'Home', 'Sports']
    
    return pd.DataFrame({
        'Дата': dates,
        'Товар': [random.choice(products) for _ in range(num_rows)],
        'Категория': [random.choice(categories) for _ in range(num_rows)],
        'Количество': np.random.randint(1, 50, num_rows),
        'Цена': np.random.uniform(10, 1000, num_rows).round(2),
        'Выручка': [0] * num_rows,  # Will calculate
    })

def generate_expenses_data(num_rows=80):
    """Generate expenses data"""
    start_date = datetime(2024, 1, 1)
    dates = [start_date + timedelta(days=i*3) for i in range(num_rows)]
    
    expense_types = ['Реклама', 'Логистика', 'Аренда', 'Зарплаты', 'Комиссии маркетплейса']
    
    return pd.DataFrame({
        'Дата': dates,
        'Тип расхода': [random.choice(expense_types) for _ in range(num_rows)],
        'Сумма': np.random.uniform(1000, 50000, num_rows).round(2),
        'Описание': [f'Платеж #{i}' for i in range(num_rows)],
    })

def generate_transactions_data(num_rows=150):
    """Generate transaction data"""
    start_date = datetime(2024, 1, 1)
    dates = [start_date + timedelta(hours=i*4) for i in range(num_rows)]
    
    statuses = ['Оплачен', 'В обработке', 'Доставлен', 'Отменен']
    
    return pd.DataFrame({
        'Дата и время': dates,
        'ID транзакции': [f'TXN{1000 + i}' for i in range(num_rows)],
        'Сумма': np.random.uniform(100, 5000, num_rows).round(2),
        'Статус': [random.choice(statuses) for _ in range(num_rows)],
        'Регион': [random.choice(['Москва', 'СПб', 'Екатеринбург', 'Казань']) for _ in range(num_rows)],
    })

def generate_customers_data(num_rows=200):
    """Generate customer data"""
    return pd.DataFrame({
        'ID клиента': [f'CUST{100 + i}' for i in range(num_rows)],
        'Количество заказов': np.random.randint(1, 20, num_rows),
        'Средний чек': np.random.uniform(500, 5000, num_rows).round(2),
        'Общая выручка': np.random.uniform(1000, 50000, num_rows).round(2),
        'Дата первого заказа': [datetime(2023, random.randint(1, 12), random.randint(1, 28)) for _ in range(num_rows)],
    })

def generate_products_data(num_rows=50):
    """Generate product catalog data"""
    categories = ['Electronics', 'Clothing', 'Food', 'Home', 'Sports']
    
    return pd.DataFrame({
        'SKU': [f'SKU{1000 + i}' for i in range(num_rows)],
        'Название': [f'Товар {i}' for i in range(num_rows)],
        'Категория': [random.choice(categories) for _ in range(num_rows)],
        'Цена': np.random.uniform(100, 10000, num_rows).round(2),
        'На складе': np.random.randint(0, 500, num_rows),
        'Продано (шт)': np.random.randint(0, 1000, num_rows),
    })

def generate_monthly_summary():
    """Generate monthly summary data"""
    months = pd.date_range('2024-01-01', periods=12, freq='ME')
    
    return pd.DataFrame({
        'Месяц': months,
        'Выручка': np.random.uniform(100000, 500000, 12).round(2),
        'Расходы': np.random.uniform(50000, 200000, 12).round(2),
        'Прибыль': [0] * 12,  # Will calculate
        'Количество заказов': np.random.randint(100, 1000, 12),
        'Средний чек': np.random.uniform(1000, 5000, 12).round(2),
    })

def create_test_excel(filename='test_multisheet_report.xlsx', num_sheets=30):
    """Create Excel file with multiple sheets
    
    Args:
        filename: Output filename
        num_sheets: Number of sheets to create (default 30)
    """
    print(f"📊 Creating test Excel file with {num_sheets} sheets...")
    
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        # Core sheets (realistic data)
        print("  Creating core data sheets...")
        
        # Sheet 1-5: Sales data by region
        regions = ['Москва', 'СПб', 'Екатеринбург', 'Казань', 'Нижний Новгород']
        for i, region in enumerate(regions, 1):
            df = generate_sales_data(num_rows=80 + i*10)
            df['Регион'] = region
            df['Выручка'] = df['Количество'] * df['Цена']
            df.to_excel(writer, sheet_name=f'Продажи_{region}', index=False)
            print(f"    ✅ Sheet {i}: Продажи_{region} ({len(df)} rows)")
        
        # Sheet 6: Total sales
        df_sales = generate_sales_data(num_rows=200)
        df_sales['Выручка'] = df_sales['Количество'] * df_sales['Цена']
        df_sales.to_excel(writer, sheet_name='Продажи_Всего', index=False)
        print(f"    ✅ Sheet 6: Продажи_Всего ({len(df_sales)} rows)")
        
        # Sheet 7: Expenses
        df_expenses = generate_expenses_data(num_rows=120)
        df_expenses.to_excel(writer, sheet_name='Расходы', index=False)
        print(f"    ✅ Sheet 7: Расходы ({len(df_expenses)} rows)")
        
        # Sheet 8: Transactions
        df_transactions = generate_transactions_data(num_rows=250)
        df_transactions.to_excel(writer, sheet_name='Транзакции', index=False)
        print(f"    ✅ Sheet 8: Транзакции ({len(df_transactions)} rows)")
        
        # Sheet 9: Customers
        df_customers = generate_customers_data(num_rows=300)
        df_customers.to_excel(writer, sheet_name='Клиенты', index=False)
        print(f"    ✅ Sheet 9: Клиенты ({len(df_customers)} rows)")
        
        # Sheet 10: Products
        df_products = generate_products_data(num_rows=60)
        df_products.to_excel(writer, sheet_name='Товары', index=False)
        print(f"    ✅ Sheet 10: Товары ({len(df_products)} rows)")
        
        # Sheet 11: Monthly summary
        df_monthly = generate_monthly_summary()
        df_monthly['Прибыль'] = df_monthly['Выручка'] - df_monthly['Расходы']
        df_monthly.to_excel(writer, sheet_name='Ежемесячная_сводка', index=False)
        print(f"    ✅ Sheet 11: Ежемесячная_сводка ({len(df_monthly)} rows)")
        
        # Additional sheets to reach target count
        print(f"  Creating additional sheets (12-{num_sheets})...")
        for i in range(12, num_sheets + 1):
            sheet_types = [
                ('Отчет', generate_sales_data),
                ('Данные', generate_transactions_data),
                ('Аналитика', generate_expenses_data),
            ]
            sheet_type, generator = random.choice(sheet_types)
            
            df = generator(num_rows=random.randint(30, 100))
            sheet_name = f'{sheet_type}_{i}'
            df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            if i % 5 == 0:
                print(f"    ✅ Sheets 12-{i} created...")
    
    print(f"\n✅ Excel file created: {filename}")
    print(f"📊 Total sheets: {num_sheets}")
    print(f"\nKey sheets for testing:")
    print("  - Продажи_Москва (largest sales)")
    print("  - Расходы (expenses)")
    print("  - Транзакции (transactions)")
    print("  - Клиенты (customers)")
    print("  - Ежемесячная_сводка (monthly summary)")
    
    return filename

if __name__ == '__main__':
    # Create test file
    filename = create_test_excel(num_sheets=30)
    
    print(f"\n🧪 Test file ready: {filename}")
    print("\nTo test Multi-Sheet Intelligence:")
    print("1. Upload this file to Cloud Storage:")
    print(f"   gsutil cp {filename} gs://financial-reports-ai-2024-reports/test/")
    print("\n2. Send analysis request with file_path:")
    print("   file_path: 'test/test_multisheet_report.xlsx'")
    print("\n3. System should detect 30 sheets and ask which to analyze")
