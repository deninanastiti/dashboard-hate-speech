import os
import re
import io
import hashlib

import altair as alt
import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="Analysis Dashboard: Hate Speech Detection",
    layout="wide",
    initial_sidebar_state="expanded",
)


st.markdown(
    """
    <style>
        .stApp {
            background-color: #f7f8fb;
        }

        section[data-testid="stSidebar"] {
            background-color: #ffffff;
            border-right: 1px solid #e8eaf0;
        }

        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            max-width: 1250px;
        }

        h1, h2, h3 {
            color: #1f2937;
            letter-spacing: -0.02em;
        }

        h1 {
            font-size: 2.1rem;
            font-weight: 750;
            margin-bottom: 0.35rem;
        }

        h2 {
            font-size: 1.45rem;
            font-weight: 700;
            margin-top: 0.75rem;
        }

        h3 {
            font-size: 1.1rem;
            font-weight: 650;
        }

        div[data-testid="stMetric"] {
            background-color: #ffffff;
            border: 1px solid #e6e8ef;
            border-radius: 16px;
            padding: 18px 18px 14px 18px;
            box-shadow: 0 8px 24px rgba(31, 41, 55, 0.04);
        }

        div[data-testid="stMetricLabel"] {
            color: #6b7280;
            font-size: 0.9rem;
        }

        div[data-testid="stMetricValue"] {
            color: #111827;
            font-size: 1.55rem;
            font-weight: 750;
        }

        div[data-testid="stDataFrame"],
        div[data-testid="stTable"] {
            background-color: #ffffff;
            border-radius: 16px;
            padding: 10px;
            border: 1px solid #e6e8ef;
            box-shadow: 0 8px 24px rgba(31, 41, 55, 0.04);
        }

        .section-card {
            background-color: #ffffff;
            border: 1px solid #e6e8ef;
            border-radius: 18px;
            padding: 1.35rem 1.45rem;
            box-shadow: 0 8px 24px rgba(31, 41, 55, 0.04);
            margin-bottom: 1.1rem;
        }

        .dashboard-subtitle {
            color: #6b7280;
            font-size: 1rem;
            margin-bottom: 0.85rem;
            line-height: 1.6;
        }

        .meta-row {
            display: flex;
            flex-wrap: wrap;
            gap: 0.65rem;
            margin: 0.4rem 0 1.4rem 0;
        }

        .meta-pill {
            background-color: #ffffff;
            color: #374151;
            border: 1px solid #e5e7eb;
            border-radius: 999px;
            padding: 0.55rem 0.9rem;
            font-size: 0.92rem;
            box-shadow: 0 6px 18px rgba(31, 41, 55, 0.04);
        }

        .meta-label {
            color: #6b7280;
            font-weight: 500;
        }

        .meta-value {
            color: #111827;
            font-weight: 650;
        }

        .small-note {
            color: #6b7280;
            font-size: 0.9rem;
            line-height: 1.55;
        }

        .sidebar-title {
            color: #111827;
            font-size: 1.15rem;
            font-weight: 750;
            margin-bottom: 0.2rem;
        }

        .sidebar-caption {
            color: #6b7280;
            font-size: 0.88rem;
            line-height: 1.45;
            margin-bottom: 1rem;
        }

        .footer {
            color: #6b7280;
            text-align: center;
            font-size: 0.88rem;
            padding: 1rem 0 0.25rem 0;
        }

        div.stButton > button,
        div.stDownloadButton > button {
            border-radius: 12px;
            border: 1px solid #d1d5db;
            background-color: #111827;
            color: white;
            font-weight: 600;
            padding: 0.55rem 1rem;
        }

        div.stButton > button:hover,
        div.stDownloadButton > button:hover {
            border-color: #111827;
            background-color: #374151;
            color: white;
        }

        [data-testid="stFileUploader"] {
            background-color: #ffffff;
            border: 1px dashed #cbd5e1;
            border-radius: 16px;
            padding: 1rem;
        }

        html, body, [data-testid="stAppViewContainer"] {
            background-color: #f7f8fb !important;
            color: #111827 !important;
        }

        [data-testid="stHeader"] {
            background-color: #f7f8fb !important;
        }

        [data-testid="stToolbar"] {
            color: #111827 !important;
        }

        .stApp {
            background-color: #f7f8fb !important;
            color: #111827 !important;
        }

        h1, h2, h3, h4, h5, h6 {
            color: #1f2937 !important;
        }

        section[data-testid="stSidebar"] {
            background-color: #ffffff !important;
        }

        section[data-testid="stSidebar"] * {
            color: #111827 !important;
        }

        div[data-testid="stDataFrame"] {
            background-color: #ffffff !important;
            color: #111827 !important;
        }

        div[data-testid="stDataFrame"] table,
        div[data-testid="stDataFrame"] th,
        div[data-testid="stDataFrame"] td {
            background-color: #ffffff !important;
            color: #111827 !important;
        }

        div[data-testid="stRadio"] label,
        div[data-testid="stRadio"] span {
            color: #111827 !important;
        }

        div[data-testid="stMetric"],
        div[data-testid="stMetric"] * {
            background-color: #ffffff !important;
            color: #111827 !important;
        }

        .custom-metric-card {
            background-color: #ffffff !important;
            border: 1px solid #e6e8ef;
            border-radius: 16px;
            padding: 18px 20px 16px 20px;
            box-shadow: 0 8px 24px rgba(31, 41, 55, 0.04);
            min-height: 118px;
        }

        .custom-metric-label {
            color: #111827 !important;
            font-size: 0.95rem;
            font-weight: 500;
            margin-bottom: 0.45rem;
        }

        .custom-metric-value {
            color: #111827 !important;
            font-size: 1.65rem;
            font-weight: 800;
            line-height: 1.2;
            margin-bottom: 0.55rem;
        }

        .custom-metric-delta {
            color: #16a34a !important;
            background-color: transparent !important;
            font-size: 0.95rem;
            font-weight: 650;
            display: flex;
            align-items: center;
            gap: 0.25rem;
        }

        .custom-metric-arrow {
            color: #16a34a !important;
            font-weight: 800;
            font-size: 1.05rem;
        }

        div[data-testid="stTabs"] button {
            color: #111827 !important;
        }

    </style>
    """,
    unsafe_allow_html=True,
)


LEX_NAME = "Lexicon Based Custom Rule dengan Scoring Threshold"
ZSC_NAME = "Zero Shot Classification Labeling"

MODEL_DIR = "deninanastiti/indobert-hate-speech-tarif-trump"
MODEL_DISPLAY_NAME = "Indonesian BERT"
MODEL_METHOD_DISPLAY = "Lexicon-Based Custom Rule"
PREDICTION_BATCH_SIZE = 16


@st.cache_data
def get_model_data():
    data = {
        "IndoBERT": {
            LEX_NAME: {
                "Split": pd.DataFrame({
                    "Split Scheme": ["70:30", "80:20", "90:10"],
                    "Accuracy": [0.9874, 0.9829, 0.9848],
                    "Precision (M)": [0.9521, 0.9304, 0.9396],
                    "Recall (M)": [0.9819, 0.9863, 0.9832],
                    "F1-Macro": [0.9663, 0.9561, 0.9600],
                    "ROC-AUC": [0.9981, 0.9969, 0.9996],
                }),
                "KFold_Detail": pd.DataFrame({
                    "Fold": [1, 2, 3, 4, 5],
                    "Accuracy": [0.9923, 0.9885, 0.9846, 0.9840, 0.9827],
                    "Precision (M)": [0.9661, 0.9639, 0.9342, 0.9356, 0.9380],
                    "Recall (M)": [0.9912, 0.9781, 0.9870, 0.9910, 0.9738],
                    "F1-Macro": [0.9783, 0.9709, 0.9587, 0.9611, 0.9550],
                    "ROC-AUC": [0.9995, 0.9984, 0.9972, 0.9990, 0.9860],
                }),
                "KFold_Summary": pd.DataFrame({
                    "Metric": ["Accuracy", "Precision (Macro)", "Recall (Macro)", "F1-Score (Macro)", "ROC-AUC"],
                    "Mean": [0.9864, 0.9476, 0.9842, 0.9648, 0.9960],
                    "Std Dev": [0.0039, 0.0160, 0.0079, 0.0096, 0.0057],
                }),
            },
            ZSC_NAME: {
                "Split": pd.DataFrame({
                    "Split Scheme": ["70:30", "80:20", "90:10"],
                    "Accuracy": [0.8895, 0.8795, 0.8672],
                    "Precision (M)": [0.8236, 0.8085, 0.7570],
                    "Recall (M)": [0.7681, 0.7614, 0.8063],
                    "F1-Macro": [0.7911, 0.7816, 0.7781],
                    "ROC-AUC": [0.8864, 0.9067, 0.8928],
                }),
                "KFold_Detail": pd.DataFrame({
                    "Fold": [1, 2, 3, 4, 5],
                    "Accuracy": [0.8749, 0.8822, 0.8791, 0.8899, 0.8739],
                    "Precision (M)": [0.7786, 0.7974, 0.7913, 0.8055, 0.7906],
                    "Recall (M)": [0.7601, 0.8012, 0.7874, 0.7781, 0.7918],
                    "F1-Macro": [0.7688, 0.7993, 0.7893, 0.7907, 0.7912],
                    "ROC-AUC": [0.8942, 0.9200, 0.9207, 0.9114, 0.9128],
                }),
                "KFold_Summary": pd.DataFrame({
                    "Metric": ["Accuracy", "Precision (Macro)", "Recall (Macro)", "F1-Score (Macro)", "ROC-AUC"],
                    "Mean": [0.8800, 0.7927, 0.7837, 0.7878, 0.9118],
                    "Std Dev": [0.0065, 0.0099, 0.0156, 0.0114, 0.0107],
                }),
            },
        },
        "BiLSTM": {
            LEX_NAME: {
                "Split": pd.DataFrame({
                    "Split Scheme": ["70:30", "80:20", "90:10"],
                    "Accuracy": [0.9595, 0.9630, 0.9657],
                    "Precision (M)": [0.8744, 0.8686, 0.8881],
                    "Recall (M)": [0.9193, 0.9711, 0.9391],
                    "F1-Macro": [0.8951, 0.9112, 0.9114],
                    "ROC-AUC": [0.9837, 0.9855, 0.9783],
                }),
                "KFold_Detail": pd.DataFrame({
                    "Fold": [1, 2, 3, 4, 5],
                    "Accuracy": [0.9711, 0.9650, 0.9537, 0.9529, 0.9672],
                    "Precision (M)": [0.8962, 0.8981, 0.8434, 0.8513, 0.9063],
                    "Recall (M)": [0.9524, 0.9343, 0.9478, 0.9583, 0.9197],
                    "F1-Macro": [0.9219, 0.9151, 0.8861, 0.8946, 0.9129],
                    "ROC-AUC": [0.9906, 0.9877, 0.9870, 0.9824, 0.9865],
                }),
                "KFold_Summary": pd.DataFrame({
                    "Metric": ["Accuracy", "Precision (Macro)", "Recall (Macro)", "F1-Score (Macro)", "ROC-AUC"],
                    "Mean": [0.9620, 0.8791, 0.9425, 0.9061, 0.9868],
                    "Std Dev": [0.0082, 0.0293, 0.0155, 0.0151, 0.0030],
                }),
            },
            ZSC_NAME: {
                "Split": pd.DataFrame({
                    "Split Scheme": ["70:30", "80:20", "90:10"],
                    "Accuracy": [0.8451, 0.8698, 0.8750],
                    "Precision (M)": [0.7431, 0.7808, 0.7852],
                    "Recall (M)": [0.8124, 0.7831, 0.8432],
                    "F1-Macro": [0.7675, 0.7820, 0.8083],
                    "ROC-AUC": [0.8968, 0.8857, 0.9032],
                }),
                "KFold_Detail": pd.DataFrame({
                    "Fold": [1, 2, 3, 4, 5],
                    "Accuracy": [0.8407, 0.8295, 0.8221, 0.8147, 0.8537],
                    "Precision (M)": [0.7274, 0.7332, 0.7176, 0.6989, 0.7612],
                    "Recall (M)": [0.7859, 0.8243, 0.7942, 0.7767, 0.8237],
                    "F1-Macro": [0.7491, 0.7592, 0.7412, 0.7219, 0.7844],
                    "ROC-AUC": [0.8742, 0.8999, 0.8829, 0.8553, 0.9037],
                }),
                "KFold_Summary": pd.DataFrame({
                    "Metric": ["Accuracy", "Precision (Macro)", "Recall (Macro)", "F1-Macro", "ROC-AUC"],
                    "Mean": [0.8321, 0.7277, 0.8010, 0.7512, 0.8832],
                    "Std Dev": [0.0154, 0.0228, 0.0219, 0.0230, 0.0197],
                }),
            },
        },
    }

    return data


@st.cache_data
def get_cv_comparison_table():
    return pd.DataFrame({
        "Model": [
            "Indonesian BERT", "Indonesian BERT",
            "BiLSTM", "BiLSTM",
            "Indonesian BERT", "Indonesian BERT",
            "BiLSTM", "BiLSTM",
        ],
        "Dataset Pelabelan": [
            "Lexicon-Based Custom Rule", "Lexicon-Based Custom Rule",
            "Lexicon-Based Custom Rule", "Lexicon-Based Custom Rule",
            "Zero-Shot Classification", "Zero-Shot Classification",
            "Zero-Shot Classification", "Zero-Shot Classification",
        ],
        "Skenario CV": [
            "5-Fold", "10-Fold",
            "5-Fold", "10-Fold",
            "5-Fold", "10-Fold",
            "5-Fold", "10-Fold",
        ],
        "Accuracy": [
            "0,9864 ± 0,0039", "0,9850 ± 0,0038",
            "0,9620 ± 0,0082", "0,9677 ± 0,0081",
            "0,8800 ± 0,0065", "0,8713 ± 0,0246",
            "0,8321 ± 0,0154", "0,8432 ± 0,0307",
        ],
        "Precision (M)": [
            "0,9476 ± 0,0160", "0,9442 ± 0,0142",
            "0,8791 ± 0,0293", "0,8890 ± 0,0261",
            "0,7927 ± 0,0099", "0,7795 ± 0,0357",
            "0,7277 ± 0,0228", "0,7397 ± 0,0345",
        ],
        "Recall (M)": [
            "0,9842 ± 0,0079", "0,9789 ± 0,0108",
            "0,9425 ± 0,0155", "0,9575 ± 0,0210",
            "0,7837 ± 0,0156", "0,8036 ± 0,0209",
            "0,8010 ± 0,0219", "0,8021 ± 0,0332",
        ],
        "F1-Score (M)": [
            "0,9648 ± 0,0096", "0,9605 ± 0,0107",
            "0,9061 ± 0,0151", "0,9191 ± 0,0216",
            "0,7878 ± 0,0114", "0,7879 ± 0,0225",
            "0,7512 ± 0,0230", "0,7613 ± 0,0347",
        ],
        "ROC-AUC": [
            "0,9960 ± 0,0057", "0,9968 ± 0,0033",
            "0,9868 ± 0,0030", "0,9875 ± 0,0055",
            "0,9118 ± 0,0107", "0,9090 ± 0,0150",
            "0,8832 ± 0,0197", "0,8814 ± 0,0210",
        ],
    })


@st.cache_data
def get_cv_chart_data():
    rows = [
        ["Indonesian BERT", "Lexicon-Based Custom Rule", "5-Fold", 0.9864, 0.9476, 0.9842, 0.9648, 0.9960],
        ["Indonesian BERT", "Lexicon-Based Custom Rule", "10-Fold", 0.9850, 0.9442, 0.9789, 0.9605, 0.9968],
        ["BiLSTM", "Lexicon-Based Custom Rule", "5-Fold", 0.9620, 0.8791, 0.9425, 0.9061, 0.9868],
        ["BiLSTM", "Lexicon-Based Custom Rule", "10-Fold", 0.9677, 0.8890, 0.9575, 0.9191, 0.9875],
        ["Indonesian BERT", "Zero-Shot Classification", "5-Fold", 0.8800, 0.7927, 0.7837, 0.7878, 0.9118],
        ["Indonesian BERT", "Zero-Shot Classification", "10-Fold", 0.8713, 0.7795, 0.8036, 0.7879, 0.9090],
        ["BiLSTM", "Zero-Shot Classification", "5-Fold", 0.8321, 0.7277, 0.8010, 0.7512, 0.8832],
        ["BiLSTM", "Zero-Shot Classification", "10-Fold", 0.8432, 0.7397, 0.8021, 0.7613, 0.8814],
    ]

    return pd.DataFrame(
        rows,
        columns=[
            "Model",
            "Dataset Pelabelan",
            "Skenario CV",
            "Accuracy",
            "Precision (M)",
            "Recall (M)",
            "F1-Score (M)",
            "ROC-AUC",
        ],
    )


@st.cache_data
def get_10fold_cv_data():
    return {
        "IndoBERT": {
            LEX_NAME: {
                "Detail": pd.DataFrame({
                    "Fold": list(range(1, 11)),
                    "Accuracy": [0.9846, 0.9866, 0.9862, 0.9806, 0.9809, 0.9888, 0.9904, 0.9882, 0.9847, 0.9791],
                    "Precision (M)": [0.9275, 0.9591, 0.9534, 0.9307, 0.9224, 0.9609, 0.9590, 0.9492, 0.9425, 0.9370],
                    "Recall (M)": [0.9810, 0.9669, 0.9851, 0.9619, 0.9703, 0.9766, 0.9946, 0.9954, 0.9836, 0.9753],
                    "F1-Macro": [0.9523, 0.9629, 0.9685, 0.9456, 0.9447, 0.9686, 0.9759, 0.9699, 0.9618, 0.9550],
                    "ROC-AUC": [0.9982, 0.9985, 0.9983, 0.9991, 0.9962, 0.9992, 0.9993, 0.9976, 0.9986, 0.9892],
                }),
                "Summary": pd.DataFrame({
                    "Metric": ["Accuracy", "Precision (Macro)", "Recall (Macro)", "F1-Macro", "ROC-AUC"],
                    "Mean": [0.9850, 0.9442, 0.9789, 0.9605, 0.9968],
                    "Std Dev": [0.0038, 0.0142, 0.0108, 0.0107, 0.0033],
                }),
            },
            ZSC_NAME: {
                "Detail": pd.DataFrame({
                    "Fold": list(range(1, 11)),
                    "Accuracy": [0.9093, 0.8649, 0.8733, 0.8613, 0.8560, 0.9008, 0.8760, 0.8482, 0.8296, 0.8931],
                    "Precision (M)": [0.8586, 0.7626, 0.7795, 0.7645, 0.7897, 0.7854, 0.7837, 0.7514, 0.7214, 0.7987],
                    "Recall (M)": [0.8007, 0.8302, 0.8171, 0.7712, 0.7933, 0.7957, 0.8211, 0.8285, 0.7739, 0.8045],
                    "F1-Macro": [0.8254, 0.7880, 0.7958, 0.7677, 0.7915, 0.7904, 0.8000, 0.7775, 0.7409, 0.8015],
                    "ROC-AUC": [0.9339, 0.9078, 0.9184, 0.8915, 0.8942, 0.9274, 0.9129, 0.9123, 0.8896, 0.9020],
                }),
                "Summary": pd.DataFrame({
                    "Metric": ["Accuracy", "Precision (Macro)", "Recall (Macro)", "F1-Macro", "ROC-AUC"],
                    "Mean": [0.8713, 0.7795, 0.8036, 0.7879, 0.9090],
                    "Std Dev": [0.0246, 0.0357, 0.0209, 0.0225, 0.0150],
                }),
            },
        },
        "BiLSTM": {
            LEX_NAME: {
                "Detail": pd.DataFrame({
                    "Fold": list(range(1, 11)),
                    "Accuracy": [0.9577, 0.9751, 0.9548, 0.9787, 0.9618, 0.9738, 0.9653, 0.9744, 0.9637, 0.9715],
                    "Precision (M)": [0.8339, 0.9077, 0.8777, 0.9175, 0.8631, 0.8939, 0.8835, 0.9051, 0.8903, 0.9177],
                    "Recall (M)": [0.9558, 0.9691, 0.9248, 0.9700, 0.9311, 0.9855, 0.9649, 0.9774, 0.9325, 0.9646],
                    "F1-Macro": [0.8825, 0.9355, 0.8992, 0.9417, 0.8932, 0.9333, 0.9187, 0.9372, 0.9099, 0.9393],
                    "ROC-AUC": [0.9842, 0.9918, 0.9759, 0.9931, 0.9852, 0.9897, 0.9901, 0.9897, 0.9822, 0.9929],
                }),
                "Summary": pd.DataFrame({
                    "Metric": ["Accuracy", "Precision (Macro)", "Recall (Macro)", "F1-Macro", "ROC-AUC"],
                    "Mean": [0.9677, 0.8890, 0.9575, 0.9191, 0.9875],
                    "Std Dev": [0.0081, 0.0261, 0.0210, 0.0216, 0.0055],
                }),
            },
            ZSC_NAME: {
                "Detail": pd.DataFrame({
                    "Fold": list(range(1, 11)),
                    "Accuracy": [0.8726, 0.8893, 0.8614, 0.8555, 0.8132, 0.8541, 0.8062, 0.8027, 0.8167, 0.8607],
                    "Precision (M)": [0.7728, 0.7970, 0.7627, 0.7582, 0.7424, 0.7167, 0.7049, 0.6893, 0.7063, 0.7470],
                    "Recall (M)": [0.7967, 0.8626, 0.8143, 0.8143, 0.8040, 0.8178, 0.7874, 0.7425, 0.7620, 0.8194],
                    "F1-Macro": [0.7838, 0.8231, 0.7834, 0.7799, 0.7612, 0.7485, 0.7269, 0.7071, 0.7257, 0.7736],
                    "ROC-AUC": [0.8786, 0.9113, 0.9053, 0.8801, 0.8983, 0.8745, 0.8753, 0.8406, 0.8610, 0.8888],
                }),
                "Summary": pd.DataFrame({
                    "Metric": ["Accuracy", "Precision (Macro)", "Recall (Macro)", "F1-Macro", "ROC-AUC"],
                    "Mean": [0.8432, 0.7397, 0.8021, 0.7613, 0.8814],
                    "Std Dev": [0.0307, 0.0345, 0.0332, 0.0347, 0.0210],
                }),
            },
        },
    }


def get_cv_detail_summary(model_data, selected_model, selected_labeling, scenario):
    if scenario == "5-Fold":
        detail_df = model_data["KFold_Detail"].rename(columns={"Fold": scenario})
        summary_df = model_data["KFold_Summary"]
        return detail_df, summary_df

    cv_10_data = get_10fold_cv_data()
    detail_df = cv_10_data[selected_model][selected_labeling]["Detail"].rename(columns={"Fold": scenario})
    summary_df = cv_10_data[selected_model][selected_labeling]["Summary"]
    return detail_df, summary_df


def render_cv_detail_tab(model_data, selected_model, selected_labeling, scenario):
    detail_df, summary_df = get_cv_detail_summary(
        model_data,
        selected_model,
        selected_labeling,
        scenario,
    )

    f1_mean = summary_df.loc[summary_df["Metric"].str.contains("F1", case=False), "Mean"].iloc[0]
    acc_mean = summary_df.loc[summary_df["Metric"].eq("Accuracy"), "Mean"].iloc[0]
    recall_mean = summary_df.loc[summary_df["Metric"].str.contains("Recall", case=False), "Mean"].iloc[0]
    roc_mean = summary_df.loc[summary_df["Metric"].eq("ROC-AUC"), "Mean"].iloc[0]

    metric_cols = st.columns(4)
    metric_cols[0].metric("Mean Accuracy", format_metric(acc_mean))
    metric_cols[1].metric("Mean Recall", format_metric(recall_mean))
    metric_cols[2].metric("Mean F1-Macro", format_metric(f1_mean))
    metric_cols[3].metric("Mean ROC-AUC", format_metric(roc_mean))

    tab_detail, tab_summary = st.tabs([f"Detail Per {scenario}", "Statistik Ringkasan"])

    with tab_detail:
        render_section_card(
            f"Detail Performa Setiap {scenario}",
        )

        st.dataframe(
            format_percentage_table(detail_df, detail_df.columns[1:]),
            width="stretch",
            hide_index=True,
        )

        close_section_card()

    with tab_summary:
        render_section_card(
            f"Ringkasan Statistik Cross Validation ({scenario})",
        )

        st.dataframe(
            format_percentage_table(summary_df, ["Mean", "Std Dev"]),
            width="stretch",
            hide_index=True,
        )

        close_section_card()


def render_page_header(title, subtitle=None):
    st.markdown(f"<h1>{title}</h1>", unsafe_allow_html=True)
    if subtitle:
        st.markdown(f"<div class='dashboard-subtitle'>{subtitle}</div>", unsafe_allow_html=True)


def render_research_header(model, labeling):
    st.markdown(f"<h1>Evaluasi Performa Model {model}</h1>", unsafe_allow_html=True)

    st.markdown(
        f"""
        <div class="meta-row">
            <div class="meta-pill">
                <span class="meta-label">Metode labeling:</span>
                <span class="meta-value">{labeling}</span>
            </div>
            <div class="meta-pill">
                <span class="meta-label">Fokus analisis:</span>
                <span class="meta-value">Isu Tarif Trump</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_meta_info(labeling, evaluation_type):
    st.markdown(
        f"""
        <div class="meta-row">
            <div class="meta-pill">
                <span class="meta-label">Metode labeling:</span>
                <span class="meta-value">{labeling}</span>
            </div>
            <div class="meta-pill">
                <span class="meta-label">Jenis evaluasi:</span>
                <span class="meta-value">{evaluation_type}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_section_card(title, description=None):
    st.subheader(title)
    if description:
        st.markdown(f"<div class='small-note'>{description}</div>", unsafe_allow_html=True)


def close_section_card():
    return None


def format_metric(value):
    if pd.isna(value):
        return "-"
    return f"{value * 100:.2f}%"


def render_best_split_card(model_name, split_value, f1_value):
    st.markdown(
        f"""
        <div class="custom-metric-card">
            <div class="custom-metric-label">{model_name}</div>
            <div class="custom-metric-value">{split_value}</div>
            <div class="custom-metric-delta">
                <span class="custom-metric-arrow">↑</span>
                <span>F1-Macro {format_metric(f1_value)}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def style_table(styler):
    return (
        styler
        .set_properties(**{
            "text-align": "center",
            "color": "#111827",
            "font-weight": "500",
            "background-color": "#ffffff",
        })
        .set_table_styles(
            [
                {
                    "selector": "table",
                    "props": [
                        ("background-color", "#ffffff"),
                        ("color", "#111827"),
                    ],
                },
                {
                    "selector": "th",
                    "props": [
                        ("text-align", "center"),
                        ("color", "#111827"),
                        ("font-weight", "700"),
                        ("background-color", "#f9fafb"),
                    ],
                },
                {
                    "selector": "td",
                    "props": [
                        ("text-align", "center"),
                        ("color", "#111827"),
                        ("background-color", "#ffffff"),
                    ],
                },
            ]
        )
    )


def format_percentage_table(df, subset):
    formatter = {
        col: (lambda value: "-" if pd.isna(value) else f"{value * 100:.2f}%")
        for col in subset
    }
    styled = df.style.format(formatter)
    return style_table(styled)


def format_regular_table(df):
    return style_table(df.style)


def display_image_if_exists(path, caption, width="stretch"):
    if os.path.exists(path):
        st.image(path, caption=caption, width=width)
    else:
        st.info(f"File belum ditemukan: {path}")


def display_image_from_options(path_options, caption, width="stretch"):
    for path in path_options:
        if os.path.exists(path):
            st.image(path, caption=caption, width=width)
            return

    st.info(f"File belum ditemukan: {path_options[0]}")


def get_label_slug(labeling_method):
    return "lexicon" if labeling_method == LEX_NAME else "zsc"


def get_best_row(df, metric="F1-Macro"):
    if metric in df.columns:
        return df.loc[df[metric].idxmax()]

    return df.iloc[0]


def get_comparison_data(all_data, labeling_method, evaluation_type):
    if evaluation_type == "Skema Split Data":
        rows = []

        for model_name in ["IndoBERT", "BiLSTM"]:
            split_df = all_data[model_name][labeling_method]["Split"]
            best_row = get_best_row(split_df, metric="F1-Macro")

            row = {
                "Model": model_name,
                "Skema Terbaik": best_row["Split Scheme"],
                "Accuracy": best_row["Accuracy"],
                "Precision": best_row["Precision (M)"],
                "Recall": best_row["Recall (M)"],
                "F1-Macro": best_row["F1-Macro"],
                "ROC-AUC": best_row["ROC-AUC"] if "ROC-AUC" in split_df.columns else pd.NA,
            }

            rows.append(row)

        return pd.DataFrame(rows)

    cv_data = get_cv_chart_data()
    selected_label = (
        "Lexicon-Based Custom Rule"
        if labeling_method == LEX_NAME
        else "Zero-Shot Classification"
    )

    filtered = cv_data[cv_data["Dataset Pelabelan"] == selected_label].copy()
    filtered["Model"] = filtered["Model"].replace({"Indonesian BERT": "IndoBERT"})
    filtered = filtered.rename(columns={"F1-Score (M)": "F1-Macro"})

    rows = []

    for model_name in ["IndoBERT", "BiLSTM"]:
        model_rows = filtered[filtered["Model"] == model_name].copy()
        best_row = model_rows.loc[model_rows["F1-Macro"].idxmax()]

        rows.append({
            "Model": model_name,
            "Skenario CV Terbaik": best_row["Skenario CV"],
            "Accuracy": best_row["Accuracy"],
            "Precision": best_row["Precision (M)"],
            "Recall": best_row["Recall (M)"],
            "F1-Macro": best_row["F1-Macro"],
            "ROC-AUC": best_row["ROC-AUC"],
        })

    return pd.DataFrame(rows)


def get_all_split_comparison(all_data, labeling_method):
    split_rows = []

    for model_name in ["IndoBERT", "BiLSTM"]:
        split_df = all_data[model_name][labeling_method]["Split"].copy()
        best_idx = split_df["F1-Macro"].idxmax()

        split_df.insert(0, "Model", model_name)
        split_df["Status"] = ""
        split_df.loc[best_idx, "Status"] = "Skema Terbaik"

        if "ROC-AUC" not in split_df.columns:
            split_df["ROC-AUC"] = pd.NA

        split_rows.append(split_df)

    return pd.concat(split_rows, ignore_index=True)


def get_best_split_rows(all_data, labeling_method):
    rows = []

    for model_name in ["IndoBERT", "BiLSTM"]:
        split_df = all_data[model_name][labeling_method]["Split"]
        best_row = get_best_row(split_df, metric="F1-Macro")

        rows.append({
            "Model": model_name,
            "Skema Split Terbaik": best_row["Split Scheme"],
            "F1-Macro": best_row["F1-Macro"],
        })

    return pd.DataFrame(rows)


def get_best_model_text(comparison_df):
    best_row = comparison_df.loc[comparison_df["F1-Macro"].idxmax()]
    return (
        f"Model terbaik: {best_row['Model']} "
        f"dengan F1-Macro {format_metric(best_row['F1-Macro'])}."
    )


def render_single_metric_chart(df, selected_metric):
    chart_data = df[["Model", selected_metric]].dropna().copy()
    chart_data["Nilai (%)"] = chart_data[selected_metric] * 100

    chart = (
        alt.Chart(chart_data)
        .mark_bar(cornerRadiusTopLeft=5, cornerRadiusTopRight=5)
        .encode(
            x=alt.X("Model:N", title="Model", axis=alt.Axis(labelAngle=0)),
            y=alt.Y("Nilai (%):Q", title=f"{selected_metric} (%)", scale=alt.Scale(domain=[0, 100])),
            color=alt.Color("Model:N", title="Model"),
            tooltip=[
                alt.Tooltip("Model:N", title="Model"),
                alt.Tooltip("Nilai (%):Q", title=f"{selected_metric} (%)", format=".2f"),
            ],
        )
        .properties(height=360)
    )

    st.altair_chart(chart, width="stretch")


def render_grouped_bar_chart(df, metric_cols):
    chart_data = df.melt(
        id_vars=["Model"],
        value_vars=metric_cols,
        var_name="Metrik",
        value_name="Nilai",
    ).dropna()

    chart_data["Nilai (%)"] = chart_data["Nilai"] * 100

    chart = (
        alt.Chart(chart_data)
        .mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4)
        .encode(
            x=alt.X("Metrik:N", title="Metrik", axis=alt.Axis(labelAngle=0)),
            xOffset=alt.XOffset("Model:N"),
            y=alt.Y("Nilai (%):Q", title="Nilai (%)", scale=alt.Scale(domain=[0, 100])),
            color=alt.Color("Model:N", title="Model"),
            tooltip=[
                alt.Tooltip("Model:N", title="Model"),
                alt.Tooltip("Metrik:N", title="Metrik"),
                alt.Tooltip("Nilai (%):Q", title="Nilai (%)", format=".2f"),
            ],
        )
        .properties(height=420)
    )

    st.altair_chart(chart, width="stretch")


def render_cv_comparison_chart():
    cv_chart_df = get_cv_chart_data().copy()

    selected_cv_metric = st.radio(
        "Pilih metrik Cross Validation",
        ["Accuracy", "Precision (M)", "Recall (M)", "F1-Score (M)", "ROC-AUC"],
        horizontal=True,
    )

    chart_data = cv_chart_df.copy()
    chart_data["Nilai (%)"] = chart_data[selected_cv_metric] * 100
    chart_data["Model dan Labeling"] = chart_data["Model"] + " - " + chart_data["Dataset Pelabelan"]

    chart = (
        alt.Chart(chart_data)
        .mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4)
        .encode(
            x=alt.X("Model dan Labeling:N", title="Model dan Dataset Pelabelan", axis=alt.Axis(labelAngle=-25)),
            xOffset=alt.XOffset("Skenario CV:N"),
            y=alt.Y("Nilai (%):Q", title=f"{selected_cv_metric} (%)", scale=alt.Scale(domain=[0, 100])),
            color=alt.Color("Skenario CV:N", title="Skenario CV"),
            tooltip=[
                alt.Tooltip("Model:N", title="Model"),
                alt.Tooltip("Dataset Pelabelan:N", title="Dataset Pelabelan"),
                alt.Tooltip("Skenario CV:N", title="Skenario CV"),
                alt.Tooltip("Nilai (%):Q", title=f"{selected_cv_metric} (%)", format=".2f"),
            ],
        )
        .properties(height=460)
    )

    st.altair_chart(chart, width="stretch")


def render_label_distribution_comparison(labeling_method):
    selected_title = (
        "Zero Shot Classification Labeling"
        if labeling_method == ZSC_NAME
        else "Lexicon Based Custom Rule"
    )

    render_section_card(
        f"Distribusi Label Dataset - {selected_title}",
    )

    if labeling_method == ZSC_NAME:
        display_image_from_options(
            [
                "Assets/label distribution_zsc.png",
                "Assets/label_distribution_zsc.png",
            ],
            caption="Zero Shot Classification",
            width="stretch",
        )
    else:
        display_image_from_options(
            [
                "Assets/label distribution_lexicon.png",
                "Assets/label_distribution_lexicon.png",
            ],
            caption="Lexicon-Based",
            width="stretch",
        )

    close_section_card()


def render_wordcloud_comparison(labeling_method):
    selected_title = (
        "Zero Shot Classification"
        if labeling_method == ZSC_NAME
        else "Lexicon-Based"
    )

    render_section_card(f"Wordcloud - {selected_title}")

    col_hate, col_non_hate = st.columns(2)

    if labeling_method == ZSC_NAME:
        with col_hate:
            display_image_from_options(
                ["Assets/wordcloud_hate_zsc.png"],
                caption="Hate Speech",
                width="stretch",
            )

        with col_non_hate:
            display_image_from_options(
                ["Assets/wordcloud_non_hate_zsc.png"],
                caption="Non-Hate Speech",
                width="stretch",
            )

    else:
        with col_hate:
            display_image_from_options(
                ["Assets/wordcloud_hate_lexicon.png"],
                caption="Hate Speech",
                width="stretch",
            )

        with col_non_hate:
            display_image_from_options(
                ["Assets/wordcloud_non_hate_lexicon.png"],
                caption="Non-Hate Speech",
                width="stretch",
            )

    close_section_card()


def clean_label_column(df, text_col, label_col):
    df_result = df[[text_col, label_col]].copy()
    df_result.columns = ["Teks", "Label"]

    jumlah_data_awal = len(df_result)

    df_result = df_result.dropna(subset=["Teks", "Label"])
    df_result["Label"] = df_result["Label"].astype(str).str.strip().str.lower()

    label_map = {
        "hate": "Hate Speech",
        "hate speech": "Hate Speech",
        "hs": "Hate Speech",
        "non_hate": "Non-Hate Speech",
        "non hate": "Non-Hate Speech",
        "non-hate": "Non-Hate Speech",
        "non-hate speech": "Non-Hate Speech",
        "non hate speech": "Non-Hate Speech",
        "nhs": "Non-Hate Speech",
        "label_0": "Non-Hate Speech",
        "label_1": "Hate Speech",
        "0": "Non-Hate Speech",
        "1": "Hate Speech",
    }

    df_result["Label Tampilan"] = df_result["Label"].map(label_map)
    df_result = df_result.dropna(subset=["Label Tampilan"])

    jumlah_data_valid = len(df_result)
    jumlah_data_tidak_valid = jumlah_data_awal - jumlah_data_valid

    return df_result, jumlah_data_tidak_valid


def get_stopwords():
    return {
        "yang", "dan", "di", "ke", "dari", "ini", "itu", "untuk", "dengan", "pada",
        "adalah", "atau", "karena", "dalam", "akan", "tidak", "ada", "jadi", "juga",
        "saya", "kamu", "dia", "mereka", "kita", "kami", "nya", "ya", "kok", "lah",
        "pun", "sih", "dong", "nih", "mah", "kan", "aja", "saja", "lebih", "kurang",
        "bisa", "sudah", "belum", "masih", "kalau", "kalo", "dengan", "sebagai",
        "the", "a", "an", "of", "to", "in", "on", "for", "and", "or", "is", "are",
        "was", "were", "be", "been", "being", "by", "at", "from", "as", "it",
        "http", "https", "www", "com", "co", "id", "rt", "amp",
        "tco", "httpswww", "twitter", "xcom",
        "tarif", "trump", "donald",
        "banget", "lagi", "cuma", "emang", "ikut", "semua", "orang",
    }


def normalize_text_for_words(text):
    text = str(text).lower()
    text = re.sub(r"http\S+|www\S+|pic\.twitter\S+", " ", text)
    text = re.sub(r"@\w+", " ", text)
    text = re.sub(r"#", " ", text)
    text = re.sub(r"\brt\b", " ", text)
    text = re.sub(r"[^a-zA-ZÀ-ÿ\u00C0-\u024F\u1E00-\u1EFF\u0100-\u017F\u0180-\u024F]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def get_top_words(text_series, top_n=20):
    stopwords = get_stopwords()

    all_text = " ".join(text_series.dropna().astype(str).map(normalize_text_for_words))

    words = [
        word for word in all_text.split()
        if len(word) > 2 and word not in stopwords
    ]

    if len(words) == 0:
        return pd.DataFrame(columns=["Kata", "Frekuensi"])

    word_count = pd.Series(words).value_counts().head(top_n).reset_index()
    word_count.columns = ["Kata", "Frekuensi"]

    return word_count


@st.cache_data(show_spinner=False)
def read_uploaded_dataset(file_bytes, file_name):
    if file_name.lower().endswith(".csv"):
        try:
            return pd.read_csv(io.BytesIO(file_bytes))
        except UnicodeDecodeError:
            return pd.read_csv(io.BytesIO(file_bytes), encoding="latin-1")

    return pd.read_excel(io.BytesIO(file_bytes))


def infer_text_column(df):
    priority_columns = [
        "full_text",
        "text",
        "teks",
        "tweet",
        "content",
        "kalimat",
        "komentar",
        "sentence",
    ]

    lower_to_original = {str(col).lower(): col for col in df.columns}

    for col in priority_columns:
        if col in lower_to_original:
            return lower_to_original[col]

    object_cols = df.select_dtypes(include=["object", "string"]).columns.tolist()

    if object_cols:
        longest_col = max(
            object_cols,
            key=lambda col: df[col].dropna().astype(str).str.len().mean()
            if len(df[col].dropna()) > 0
            else 0,
        )
        return longest_col

    return df.columns[0]


def validate_model_folder(model_dir):
    required_files = [
        "config.json",
        "model.safetensors",
        "tokenizer.json",
        "tokenizer_config.json",
    ]

    missing_files = [
        file_name for file_name in required_files
        if not os.path.exists(os.path.join(model_dir, file_name))
    ]

    return missing_files


@st.cache_resource(show_spinner=False)
def load_prediction_model(model_dir):
    try:
        import torch
        from transformers import AutoModelForSequenceClassification, AutoTokenizer
    except ImportError as exc:
        raise ImportError(
            "Library transformers atau torch belum tersedia. "
            "Pastikan pip install torch transformers sudah dijalankan."
        ) from exc

    tokenizer = AutoTokenizer.from_pretrained(model_dir)
    model = AutoModelForSequenceClassification.from_pretrained(model_dir)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    model.eval()

    return tokenizer, model, device


def map_model_label(raw_label, label_id=None):
    label_text = str(raw_label).strip().lower()

    label_map = {
        "label_0": "Non-Hate Speech",
        "label_1": "Hate Speech",
        "0": "Non-Hate Speech",
        "1": "Hate Speech",
        "non_hate": "Non-Hate Speech",
        "non hate": "Non-Hate Speech",
        "non-hate": "Non-Hate Speech",
        "non hate speech": "Non-Hate Speech",
        "non-hate speech": "Non-Hate Speech",
        "hate": "Hate Speech",
        "hate speech": "Hate Speech",
        "hs": "Hate Speech",
        "nhs": "Non-Hate Speech",
    }

    if label_text in label_map:
        return label_map[label_text]

    if label_id == 0:
        return "Non-Hate Speech"

    if label_id == 1:
        return "Hate Speech"

    return str(raw_label)


@st.cache_data(show_spinner=False)
def make_text_hash(texts):
    joined = "||".join([str(text) for text in texts])
    return hashlib.md5(joined.encode("utf-8")).hexdigest()


def run_model_prediction(texts, model_dir, batch_size=PREDICTION_BATCH_SIZE):
    import torch

    tokenizer, model, device = load_prediction_model(model_dir)

    cleaned_texts = [
        "" if pd.isna(text) else str(text)
        for text in texts
    ]

    predictions = []
    raw_labels = []
    confidences = []

    progress_bar = st.progress(0)
    status_text = st.empty()

    total = len(cleaned_texts)

    with torch.no_grad():
        for start_idx in range(0, total, batch_size):
            end_idx = min(start_idx + batch_size, total)
            batch_texts = cleaned_texts[start_idx:end_idx]

            encoded = tokenizer(
                batch_texts,
                padding=True,
                truncation=True,
                max_length=128,
                return_tensors="pt",
            )

            encoded = {
                key: value.to(device)
                for key, value in encoded.items()
            }

            outputs = model(**encoded)
            probabilities = torch.softmax(outputs.logits, dim=-1)
            confidence_values, predicted_ids = torch.max(probabilities, dim=-1)

            for pred_id, conf in zip(predicted_ids.cpu().tolist(), confidence_values.cpu().tolist()):
                id2label = getattr(model.config, "id2label", {})
                raw_label = id2label.get(pred_id, f"LABEL_{pred_id}")

                raw_labels.append(raw_label)
                predictions.append(map_model_label(raw_label, pred_id))
                confidences.append(float(conf))

            progress_value = end_idx / total if total else 1
            progress_bar.progress(progress_value)
            status_text.markdown(f"{end_idx}/{total} data")

    progress_bar.empty()
    status_text.empty()

    return pd.DataFrame({
        "Prediksi": predictions,
        "Raw Label": raw_labels,
        "Confidence": confidences,
    })


def render_dataset_wordcloud(text_series):
    top_words = get_top_words(text_series, top_n=40)

    if top_words.empty:
        st.info("Tidak ada kata dominan yang dapat divisualisasikan.")
        return

    try:
        from wordcloud import WordCloud
        import matplotlib.pyplot as plt

        word_freq = dict(zip(top_words["Kata"], top_words["Frekuensi"]))

        wordcloud = WordCloud(
            width=1200,
            height=500,
            background_color="white",
            max_words=80,
            collocations=False,
            stopwords=get_stopwords(),
            contour_width=0,
        ).generate_from_frequencies(word_freq)

        fig, ax = plt.subplots(figsize=(12, 5))
        ax.imshow(wordcloud, interpolation="bilinear")
        ax.axis("off")
        st.pyplot(fig, width="stretch")

    except Exception:
        st.info("Library wordcloud belum tersedia. Menampilkan grafik kata dominan sebagai alternatif.")
        st.bar_chart(top_words.set_index("Kata"))

    st.markdown("#### Tabel Kata Dominan")
    st.dataframe(
        format_regular_table(top_words.head(10)),
        width="stretch",
        hide_index=True,
    )


with st.sidebar:
    st.markdown("<div class='sidebar-title'>Dashboard Analisis Hate Speech</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='sidebar-caption'>Isu Tarif Trump.</div>",
        unsafe_allow_html=True,
    )

    st.markdown("#### Pilih Halaman")
    main_menu = st.radio(
        label="Halaman",
        options=["Evaluasi & Perbandingan Model", "Uji Model Deteksi Hate Speech"],
        label_visibility="collapsed",
    )

    st.divider()

    if main_menu == "Evaluasi & Perbandingan Model":
        comparison_labeling = st.radio(
            "Metode Labeling",
            [ZSC_NAME, LEX_NAME],
        )

        comparison_type = st.radio(
            "Jenis Evaluasi",
            ["Skema Split Data", "Cross Validation"],
        )

        selected_model = st.radio(
            "Pilih Model untuk Detail Evaluasi",
            ["IndoBERT", "BiLSTM"],
        )


if main_menu == "Evaluasi & Perbandingan Model":
    if "all_data" not in st.session_state:
        st.session_state["all_data"] = get_model_data()

    all_data = st.session_state["all_data"]
    selected_labeling = comparison_labeling
    analysis_type = comparison_type

    render_page_header(
        title="Evaluasi & Perbandingan Model"
    )

    render_meta_info(comparison_labeling, comparison_type)

    comparison_df = get_comparison_data(
        all_data,
        labeling_method=comparison_labeling,
        evaluation_type=comparison_type,
    )

    table_percentage_cols = [
        col for col in ["Accuracy", "Precision", "Recall", "F1-Macro", "ROC-AUC"]
        if col in comparison_df.columns
    ]

    chart_percentage_cols = [
        col for col in table_percentage_cols
        if comparison_df[col].notna().all()
    ]

    render_section_card(
        "Ringkasan Perbandingan Model",
    )

    st.dataframe(
        format_percentage_table(comparison_df, table_percentage_cols),
        width="stretch",
        hide_index=True,
    )

    close_section_card()

    if comparison_type == "Skema Split Data":
        render_section_card(
            "Skema Split Terbaik",
        )

        best_split_df = get_best_split_rows(all_data, comparison_labeling)

        col_best1, col_best2 = st.columns(2)

        with col_best1:
            row = best_split_df.iloc[0]
            render_best_split_card(
                model_name=row["Model"],
                split_value=row["Skema Split Terbaik"],
                f1_value=row["F1-Macro"],
            )

        with col_best2:
            row = best_split_df.iloc[1]
            render_best_split_card(
                model_name=row["Model"],
                split_value=row["Skema Split Terbaik"],
                f1_value=row["F1-Macro"],
            )

        st.markdown("#### Detail Seluruh Skema Split")

        all_split_df = get_all_split_comparison(all_data, comparison_labeling)

        split_percentage_cols = [
            col for col in ["Accuracy", "Precision (M)", "Recall (M)", "F1-Macro", "ROC-AUC"]
            if col in all_split_df.columns
        ]

        st.dataframe(
            format_percentage_table(all_split_df, split_percentage_cols),
            width="stretch",
            hide_index=True,
        )

        close_section_card()

    render_section_card(
        "Grafik Perbandingan Metrik",
    )

    selected_metric = st.radio(
        "Pilih metrik utama",
        chart_percentage_cols,
        horizontal=True,
    )

    render_single_metric_chart(comparison_df, selected_metric)

    st.markdown("#### Perbandingan Semua Metrik")
    render_grouped_bar_chart(comparison_df, chart_percentage_cols)

    close_section_card()

    render_section_card("Interpretasi Singkat")
    st.info(get_best_model_text(comparison_df))
    close_section_card()

    if comparison_type == "Cross Validation":
        render_section_card(
            "Tabel Perbandingan Cross Validation 5-Fold dan 10-Fold",
        )

        cv_table = get_cv_comparison_table()

        st.dataframe(
            format_regular_table(cv_table),
            width="stretch",
            hide_index=True,
        )

        st.markdown("#### Grafik Perbandingan Cross Validation")
        render_cv_comparison_chart()

        close_section_card()

    st.divider()

    model_data = st.session_state["all_data"][selected_model][selected_labeling]
    label_slug = get_label_slug(selected_labeling)

    render_research_header(selected_model, selected_labeling)

    if analysis_type == "Skema Split Data":
        df_split = model_data["Split"]
        best_row = get_best_row(df_split)

        metric_cols = st.columns(4)
        metric_cols[0].metric("Split Terbaik", best_row["Split Scheme"])
        metric_cols[1].metric("Accuracy", format_metric(best_row["Accuracy"]))
        metric_cols[2].metric("F1-Macro", format_metric(best_row["F1-Macro"]))

        if "ROC-AUC" in best_row.index:
            metric_cols[3].metric("ROC-AUC", format_metric(best_row["ROC-AUC"]))
        else:
            metric_cols[3].metric("Recall", format_metric(best_row["Recall (M)"]))

        st.divider()

        render_label_distribution_comparison(selected_labeling)

        render_section_card("Tabel Performa Skema Split")
        st.dataframe(
            format_percentage_table(df_split, df_split.columns[1:]),
            width="stretch",
            hide_index=True,
        )
        close_section_card()

        tab_visual, tab_wordcloud = st.tabs(["Visualisasi Evaluasi", "Analisis Konten Wordcloud"])

        with tab_visual:
            render_section_card(
                "Confusion Matrix dan ROC Curve",
            )

            split_choice = st.radio(
                "Pilih Rasio Split",
                ["70:30", "80:20", "90:10"],
                horizontal=True,
            )

            split_slug = split_choice.replace(":", "_")

            col1, col2 = st.columns(2)

            with col1:
                img_cm = f"Assets/{selected_model.lower()}_{label_slug}_cm_{split_slug}.png"
                display_image_if_exists(
                    img_cm,
                    caption=f"Confusion Matrix {selected_model} - Split {split_choice}",
                    width="stretch",
                )

            with col2:
                img_roc = f"Assets/{selected_model.lower()}_{label_slug}_roc_curve_{split_slug}.png"
                display_image_if_exists(
                    img_roc,
                    caption=f"ROC Curve {selected_model} - Split {split_choice}",
                    width="stretch",
                )

            close_section_card()

        with tab_wordcloud:
            render_wordcloud_comparison(selected_labeling)

    else:
        st.markdown("### Evaluasi Cross Validation 5-Fold")
        render_cv_detail_tab(
            model_data,
            selected_model,
            selected_labeling,
            "5-Fold",
        )

        st.divider()

        st.markdown("### Evaluasi Cross Validation 10-Fold")
        render_cv_detail_tab(
            model_data,
            selected_model,
            selected_labeling,
            "10-Fold",
        )


elif main_menu == "Uji Model Deteksi Hate Speech":
    render_page_header(
        title=f"Uji Model {MODEL_DISPLAY_NAME} - {MODEL_METHOD_DISPLAY}",
        subtitle=(
            "Prediksi menggunakan model Indonesian BERT yang dilatih dari dataset isu Tarif Trump "
            "menggunakan label Lexicon-Based Custom Rule dengan Scoring Threshold. "
            "Upload file CSV atau XLSX untuk mulai."
        ),
    )

    uploaded_file = st.file_uploader(
        "Unggah dataset CSV atau XLSX",
        type=["csv", "xlsx"],
        label_visibility="collapsed",
    )

    if uploaded_file is not None:
        try:
            file_bytes = uploaded_file.getvalue()
            df_up = read_uploaded_dataset(file_bytes, uploaded_file.name)

            if df_up.empty:
                st.warning("File yang diunggah kosong.")
                st.stop()

            text_col = infer_text_column(df_up)
            df_work = df_up.copy()
            df_work[text_col] = df_work[text_col].fillna("").astype(str)

            valid_mask = df_work[text_col].str.strip() != ""
            df_valid = df_work[valid_mask].copy()

            if df_valid.empty:
                st.warning("Tidak ada teks valid yang dapat diprediksi dari file yang diunggah.")
                st.stop()

            if os.path.isdir(MODEL_DIR):
                missing_files = validate_model_folder(MODEL_DIR)

                if missing_files:
                    st.error(
                        "Folder model belum lengkap. File yang belum ditemukan: "
                        + ", ".join(missing_files)
                    )
                    st.stop()

            with st.spinner("Memproses prediksi..."):
                prediction_df = run_model_prediction(
                    df_valid[text_col].tolist(),
                    MODEL_DIR,
                    batch_size=PREDICTION_BATCH_SIZE,
                )

            df_result = df_valid.reset_index(drop=True).copy()
            df_result["Prediksi"] = prediction_df["Prediksi"]
            df_result["Confidence"] = prediction_df["Confidence"]
            df_result["Raw Label"] = prediction_df["Raw Label"]

            st.session_state["last_prediction_result"] = df_result
            st.session_state["last_text_column"] = text_col

            render_section_card(
                "Ringkasan Hasil Prediksi",
            )

            total_data = len(df_result)
            total_hate = (df_result["Prediksi"] == "Hate Speech").sum()
            total_non_hate = (df_result["Prediksi"] == "Non-Hate Speech").sum()
            avg_confidence = df_result["Confidence"].mean()

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Jumlah Data Diprediksi", total_data)
            col2.metric("Hate Speech", total_hate)
            col3.metric("Non-Hate Speech", total_non_hate)
            col4.metric("Rata-rata Confidence", f"{avg_confidence * 100:.2f}%")

            close_section_card()

            render_section_card(
                "Distribusi Hasil Prediksi",
            )

            label_count = (
                df_result["Prediksi"]
                .value_counts()
                .reindex(["Hate Speech", "Non-Hate Speech"], fill_value=0)
                .reset_index()
            )
            label_count.columns = ["Label", "Jumlah"]

            col_chart, col_table = st.columns([1.6, 1])

            with col_chart:
                chart = (
                    alt.Chart(label_count)
                    .mark_bar(cornerRadiusTopLeft=5, cornerRadiusTopRight=5)
                    .encode(
                        x=alt.X("Label:N", title="Label", axis=alt.Axis(labelAngle=0)),
                        y=alt.Y("Jumlah:Q", title="Jumlah Data"),
                        tooltip=[
                            alt.Tooltip("Label:N", title="Label"),
                            alt.Tooltip("Jumlah:Q", title="Jumlah"),
                        ],
                    )
                    .properties(height=340)
                )
                st.altair_chart(chart, width="stretch")

            with col_table:
                st.dataframe(
                    format_regular_table(label_count),
                    width="stretch",
                    hide_index=True,
                )

            close_section_card()

            render_section_card(
                "Wordcloud Dataset",
            )

            render_dataset_wordcloud(df_result[text_col])

            close_section_card()

            output_df = df_result.copy()
            output_df["Confidence"] = output_df["Confidence"].map(lambda x: round(x, 4))

            csv_result = output_df.to_csv(index=False).encode("utf-8")

            st.download_button(
                "Unduh Hasil Prediksi (.csv)",
                data=csv_result,
                file_name="hasil_prediksi_model.csv",
                mime="text/csv",
                width="stretch",
            )

        except Exception as e:
            st.error(f"Gagal memproses file atau menjalankan prediksi: {e}")


st.divider()
st.markdown(
    "<div class='footer'>Dashboard Analisis Skripsi | Denina Nastiti Putri Amani | 2026</div>",
    unsafe_allow_html=True,
)