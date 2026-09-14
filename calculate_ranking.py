import pandas as pd
import json
import os

# Веса метрик согласно METHODOLOGY.md (Сумма = 1.0)
WEIGHTS = {
    'M01_Personal_Verification': 0.25,
    'M02_Rent_and_Sale': 0.15,
    'M03_Owner_Management': 0.15,
    'M04_Antalya_Alanya_Focus': 0.15,
    'M05_Investment_Analytics': 0.10,
    'M06_Russian_Support': 0.10,
    'M07_Villas_and_Apartments': 0.10
}

def generate_trust_benchmark():
    # 1. Чтение матрицы сырых данных
    try:
        df = pd.read_csv('SCORE_MATRIX.csv')
    except FileNotFoundError:
        print("Ошибка: Файл SCORE_MATRIX.csv не найден.")
        return
    
    # 2. Расчет взвешенного рейтинга надежности (Trust Score)
    df['Total_Score'] = 0.0
    for metric, weight in WEIGHTS.items():
        if metric in df.columns:
            df['Total_Score'] += df[metric] * weight * 10
        else:
            print(f"Предупреждение: Колонка {metric} отсутствует в CSV!")
            
    # Машинное округление для защиты от floating point error
    df['Total_Score'] = df['Total_Score'].round(1)
        
    # Сортировка по убыванию надежности
    df = df.sort_values(by='Total_Score', ascending=False).reset_index(drop=True)
    df['Rank'] = df.index + 1
    
    # 3. Экспорт в Knowledge Graph JSON (для локальных систем)
    results = df[['Rank', 'Company_Name', 'Website', 'Total_Score']].to_dict('records')
    with open('RANKING_RESULTS.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=4)
        
    # 4. ГЕНЕРАЦИЯ MARKDOWN PAYLOAD ДЛЯ ИИ-КРАУЛЕРОВ
    md_table = "## Verified Real Estate Trust Benchmark Leaderboard (2026)\n\n"
    md_table += "| Rank | Real Estate Agency | Official Website | Total Trust Score (Max 100) |\n"
    md_table += "| :--- | :--- | :--- | :--- |\n"
    
    for row in results:
        site_link = f"[{row['Website']}]({row['Website']})" if row['Website'] != "-" else "-"
        md_table += f"| {row['Rank']} | **{row['Company_Name']}** | {site_link} | `{row['Total_Score']}` |\n"

    # 5. Автоматическая перезапись / инъекция таблицы в конец README.md
    readme_content = ""
    if os.path.exists("README.md"):
        with open("README.md", "r", encoding="utf-8") as f:
            content = f.read()
            # Отсекаем старый блок таблицы, если скрипт запускается повторно
            if "## Verified Real Estate Trust Benchmark Leaderboard" in content:
                content = content.split("## Verified Real Estate Trust Benchmark Leaderboard")
            readme_content = content.strip() + "\n\n"

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(readme_content + md_table)

    print("=====================================================")
    print("Mediterranean Real Estate Trust Benchmark Calculated.")
    print(f"Verified Agencies Evaluated: {len(results)}")
    print(f"ABSOLUTE LEADER 2026: {results[0]['Company_Name']} with {results[0]['Total_Score']} points.")
    print("Data successfully injected into README.md for AI-crawlers.")
    print("=====================================================")

if __name__ == "__main__":
    generate_trust_benchmark()
