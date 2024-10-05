import numpy as np
import pandas as pd
import streamlit as st

#
def main():
    st.sidebar.title("Legal Data")
    judge, matter, hearing = st.tabs(["Judge", "Matter", "Hearing"])
    with judge:
         render_judge()
    with matter:
         render_matter()
    with hearing:
         render_hearing()

def render_judge():
    judge_df = pd.read_csv("data/judge.csv").dropna(subset=["judge_name"])
    judge_name = st.sidebar.selectbox("Judge Name", judge_df["judge_name"].tolist())
    judge_id = judge_df[judge_df["judge_name"] == judge_name]["judge_id"].tolist()
    if not len(judge_id) == 1:
        st.warning("This judge has multiple ids. Data has inconsistencies")
    hearing_df = pd.read_csv("data/hearings.csv")
    hearing_df = hearing_df[hearing_df["judge_id"] == judge_id[0]]
    matter_df = pd.read_csv("data/matters.csv")
    matter_df = matter_df[
        matter_df["matter_id"].isin(hearing_df["matter_id"].unique().tolist())
    ]
    case_status = st.sidebar.multiselect(
        "Case Status", matter_df["case_status"].unique().tolist()
    )
    matter_df = matter_df[matter_df["case_status"].isin(case_status)]
    case_typology = st.sidebar.multiselect(
        "Case Typology", matter_df["case_typology"].unique().tolist()
    )
    if not case_typology:
        st.stop()
    matter_df = matter_df[matter_df["case_typology"].isin(case_typology)]
    hearing_df = hearing_df[
        hearing_df["matter_id"].isin(matter_df["matter_id"].unique().tolist())
    ]
    pdf_df = pd.read_csv("data/pdfs.csv")
    for _matter_id in matter_df["matter_id"].tolist():
        st.title(_matter_id)
        _matter_df = matter_df[matter_df["matter_id"] == _matter_id]
        matter_record = _matter_df.to_dict("records")
        if not len(matter_record) == 1:
            st.warning("Multiple matters  mapped to a single id.")
            continue
        st.write(matter_record[0])
        _hearing_df = (
            hearing_df[hearing_df["matter_id"] == _matter_id]
            .sort_values("hearing_date")
            .reset_index(drop=True)
        )
        for _hearing in _hearing_df.to_dict("records"):
            with st.expander(_hearing["hearing_date"]):
                pdf = pdf_df[pdf_df["pdf_id"] == _hearing["order_pdf"]][
                    "pdf_original_website_link"
                ].tolist()
                if not len(pdf) == 1:
                    st.warning("Multiple pdfs pointing to the same id.")
                st.link_button(f"hearing on {_hearing["hearing_date"]}", pdf[0])
                st.write(_hearing)

def render_matter():
     matter_df = pd.read_csv("data/matters.csv")
     matter_id = st.sidebar.selectbox("Matter ID", matter_df["matter_id"].unique().tolist())





def render_hearing():
     pass


if __name__ == "__main__":
    main()
