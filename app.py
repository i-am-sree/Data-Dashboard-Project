from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np
import io
import json

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not file.filename.endswith('.csv'):
        return jsonify({'error': 'Only CSV files are supported'}), 400

    try:
        content = file.read().decode('utf-8')
        df = pd.read_csv(io.StringIO(content))

        if df.empty:
            return jsonify({'error': 'CSV file is empty'}), 400

        # --- TABLE DATA ---
        df_clean = df.where(pd.notnull(df), None)
        # Replace NaN/inf values with None for JSON serialization
        df_clean = df_clean.replace([np.nan, np.inf, -np.inf], None)
        table_data = {
            'columns': list(df.columns),
            'rows': df_clean.head(100).values.tolist(),
            'total_rows': len(df),
            'total_cols': len(df.columns)
        }

        # --- SUMMARY STATS ---
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        summary = {}
        for col in numeric_cols:
            col_data = df[col].dropna()
            if len(col_data) == 0:
                continue  # Skip columns with all NaN values
            summary[col] = {
                'mean': round(float(col_data.mean()), 2) if len(col_data) > 0 else None,
                'median': round(float(col_data.median()), 2) if len(col_data) > 0 else None,
                'std': round(float(col_data.std()), 2) if len(col_data) > 1 else None,
                'min': round(float(col_data.min()), 2) if len(col_data) > 0 else None,
                'max': round(float(col_data.max()), 2) if len(col_data) > 0 else None,
                'count': int(col_data.count()),
                'nulls': int(df[col].isnull().sum())
            }

        # --- CHART DATA ---
        charts = []

        # Bar chart for numeric columns (first 6)
        if numeric_cols:
            bar_cols = numeric_cols[:6]
            means = []
            for c in bar_cols:
                col_mean = df[c].mean()
                means.append(round(float(col_mean), 2) if pd.notna(col_mean) else None)
            charts.append({
                'id': 'bar_means',
                'type': 'bar',
                'title': 'Average Values by Column',
                'labels': bar_cols,
                'datasets': [{
                    'label': 'Mean Value',
                    'data': means
                }]
            })

        # Distribution histogram for first numeric col
        if numeric_cols:
            col = numeric_cols[0]
            values = df[col].dropna().tolist()
            # Bin into 10 buckets
            if len(values) > 1:
                try:
                    hist, bin_edges = np.histogram(values, bins=10)
                    bin_labels = [f"{round(bin_edges[i],1)}–{round(bin_edges[i+1],1)}" for i in range(len(bin_edges)-1)]
                    charts.append({
                        'id': 'histogram',
                        'type': 'bar',
                        'title': f'Distribution of {col}',
                        'labels': bin_labels,
                        'datasets': [{
                            'label': 'Frequency',
                            'data': hist.tolist()
                        }]
                    })
                except:
                    pass  # Skip histogram if calculation fails

        # Pie chart for first categorical column
        cat_cols = df.select_dtypes(include=['object']).columns.tolist()
        if cat_cols:
            col = cat_cols[0]
            vc = df[col].value_counts().head(8)
            charts.append({
                'id': 'pie_cat',
                'type': 'doughnut',
                'title': f'Breakdown: {col}',
                'labels': vc.index.tolist(),
                'datasets': [{
                    'label': 'Count',
                    'data': vc.values.tolist()
                }]
            })

        # Line chart if there are 2+ numeric cols
        if len(numeric_cols) >= 2:
            try:
                sample = df[numeric_cols[:2]].dropna().head(50)
                if len(sample) > 0:
                    charts.append({
                        'id': 'line_trend',
                        'type': 'line',
                        'title': f'{numeric_cols[0]} vs {numeric_cols[1]}',
                        'labels': list(range(1, len(sample)+1)),
                        'datasets': [
                            {'label': numeric_cols[0], 'data': sample[numeric_cols[0]].round(2).tolist()},
                            {'label': numeric_cols[1], 'data': sample[numeric_cols[1]].round(2).tolist()}
                        ]
                    })
            except:
                pass  # Skip line chart if calculation fails

        # Missing values chart
        missing = {col: int(df[col].isnull().sum()) for col in df.columns if df[col].isnull().sum() > 0}
        if missing:
            charts.append({
                'id': 'missing',
                'type': 'bar',
                'title': 'Missing Values per Column',
                'labels': list(missing.keys()),
                'datasets': [{'label': 'Missing Count', 'data': list(missing.values())}]
            })

        # --- QUICK INSIGHTS ---
        insights = []
        insights.append(f"📊 Dataset has {len(df)} rows and {len(df.columns)} columns.")
        if numeric_cols:
            top_col = max(numeric_cols, key=lambda c: df[c].mean())
            insights.append(f"📈 Highest average: '{top_col}' with mean {round(df[top_col].mean(), 2)}")
        total_nulls = int(df.isnull().sum().sum())
        if total_nulls > 0:
            insights.append(f"⚠️ {total_nulls} missing values found across the dataset.")
        else:
            insights.append("✅ No missing values — clean dataset!")
        if cat_cols:
            col = cat_cols[0]
            top_val = df[col].value_counts().idxmax()
            insights.append(f"🏆 Most common '{col}': {top_val}")

        return jsonify({
            'success': True,
            'filename': file.filename,
            'table': table_data,
            'summary': summary,
            'charts': charts,
            'insights': insights
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
