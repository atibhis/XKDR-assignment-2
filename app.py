import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
from datetime import datetime

ACTSECTION = pd.read_csv("data/actsection.csv")
COURT = pd.read_csv("data/court.csv")
HEARINGS = pd.read_csv("data/hearings.csv")
JUDGE = pd.read_csv("data/judge.csv")
MATTERS = pd.read_csv("data/matters.csv")
PDFS = pd.read_csv("data/pdfs.csv")

st.set_page_config(layout="wide")


def main():
    st.sidebar.title("Legal Data")
    view = st.sidebar.radio("View", options=["Overview", "Detail"])
    if view == "Overview":
        render_overview()
    if view == "Detail":
        render_detail()


def render_overview():
    st.write(JUDGE)
    st.write(MATTERS)
    st.write(HEARINGS)


def render_detail():
    judge, matter, acts = st.tabs(["Judge", "Matter", "Acts"])
    if judge:
        render_judge()
    if matter:
        render_matter()
    if acts:
        render_acts()

# Detailed View -- Judge
def render_judge():
    judge_df = JUDGE.copy(deep=True)
    _judge_name, _case_status, _case_typology = st.columns([3, 2, 2])
    judge_name = _judge_name.selectbox(
        "Judge Name", judge_df["judge_name"].unique().tolist()
    )

    matter_df = MATTERS.copy(deep=True)
    hearing_df = HEARINGS.copy(deep=True)
    judge_id = judge_df[judge_df["judge_name"] == judge_name]["judge_id"].tolist()
    if not len(judge_id) == 1:
        st.warn("Multiple ids for same judge")
    hearing_df = hearing_df[hearing_df["judge_id"] == judge_id[0]]
    matter_id = hearing_df["matter_id"].unique().tolist()
    matter_df = matter_df[matter_df["matter_id"].isin(matter_id)]
    case_status = _case_status.multiselect(
        "Case Status", matter_df["case_status"].unique()
    )
    if not case_status:
        st.info("Choose Case Status")
        st.stop()
    matter_df = matter_df[matter_df["case_status"].isin(case_status)]
    case_typology = _case_typology.multiselect(
        "Case Typology", matter_df["case_typology"].unique()
    )
    if not case_typology:
        st.info("Choose Case Typology")
        st.stop()
    matter_df = matter_df[matter_df["case_typology"].isin(case_typology)]
    matter_id = matter_df["matter_id"].unique().tolist()
    hearing_df = hearing_df[hearing_df["matter_id"].isin(matter_id)]
    for matter in matter_df.to_dict("records"):
        _matter_id = matter.pop("matter_id")
        _hearing_df = hearing_df[hearing_df["matter_id"] == _matter_id].sort_values("hearing_date")
        expander_name = ""
        expander_name += (
            f"Matter ID: `{return_valid(_matter_id)}`"
        )
        expander_name += (
            f", CNR: `{return_valid(matter.pop("cnr"))}`"
        )
        expander_name += (
            f", Filing Number: `{return_valid(matter.pop('filing_no'))}`"  
        )
        expander_name += (
            f", Filing Date: `{return_valid(matter.pop('filing_date'))}`" 
        )
        rname = return_valid(matter.pop('registration_number'))
        expander_name += (
            f", Registration Number: `{rname}`"
        ) if rname else ''
        rdate = return_valid(matter.pop('registration_date'))
        expander_name += (
            f", Registration Date: `{rdate}`"
        ) if rdate else ''
        matter.pop("case_status")
        matter.pop("case_typology")
        with st.expander(expander_name):
            for key, value in matter.items():
                if key == "court_id":
                    st.write(f"Court: `{COURT[COURT["court_id"]==value]["court_name"].tolist()[0]}`")
                    continue
                if key == "act_section_id":
                    st.write(f"Act section ID: `{ACTSECTION[ACTSECTION["act_section_id"]==value]["act_name"].tolist()[0]}`")
                    continue
                if (fixed_str(value) == "") or (return_valid(value)==''):
                    continue
                st.write(f"{key}: `{fixed_str(value)}`")
            for _hearing in _hearing_df.to_dict("records"):
                _hearing_text = ''
                _hearing_text+=f"Hearing ID: `{return_valid(_hearing.pop('hearing_id'))}`"
                _hearing_text+=f", Hearing Date: `{return_valid(_hearing.pop('hearing_date'))}`"
                otext = return_valid(_hearing.pop('order_text'))
                _hearing_text+=f"Order Text: `{otext}`" if otext else ''
                pdf_link = PDFS[PDFS["pdf_id"] == _hearing["order_pdf"]]["pdf_original_website_link"].tolist()[0]
                st.page_link(pdf_link, label = _hearing_text, icon = "🔗")

# Detailed view -- Matter
def render_matter():
    matter_df = MATTERS.copy(deep=True)
    _matter_id = st.columns(1)[0]
    matter_id = _matter_id.selectbox(
        "Matter ID", matter_df["matter_id"].unique().tolist()
    )

    hearing_df = HEARINGS.copy(deep=True)
    hearing_df = hearing_df[hearing_df["matter_id"] == matter_id].copy()

    matter_id = hearing_df["matter_id"].unique().tolist()
    matter_df = matter_df[matter_df["matter_id"].isin(matter_id)]

    hearing_df = hearing_df[hearing_df["matter_id"].isin(matter_id)]
    
    for matter in matter_df.to_dict("records"):
        _matter_id = matter.pop("matter_id")
        _hearing_df = hearing_df[hearing_df["matter_id"] == _matter_id].sort_values("hearing_date")
        expander_name = ""
        expander_name += (
            f"Matter ID: `{return_valid(_matter_id)}`"
        )
        expander_name += (
            f", CNR: `{return_valid(matter.pop("cnr"))}`"
        )
        expander_name += (
            f", Filing Number: `{return_valid(matter.pop('filing_no'))}`"  
        )
        expander_name += (
            f", Filing Date: `{return_valid(matter.pop('filing_date'))}`" 
        )
        rname = return_valid(matter.pop('registration_number'))
        expander_name += (
            f", Registration Number: `{rname}`"
        ) if rname else ''
        rdate = return_valid(matter.pop('registration_date'))
        expander_name += (
            f", Registration Date: `{rdate}`"
        ) if rdate else ''

        with st.expander(expander_name):
            for key, value in matter.items():
                if key == "court_id":
                    st.write(f"Court: `{COURT[COURT["court_id"]==value]["court_name"].tolist()[0]}`")
                    continue
                if key == "act_section_id":
                    st.write(f"Act section ID: `{ACTSECTION[ACTSECTION["act_section_id"]==value]["act_name"].tolist()[0]}`")
                    continue
                if (fixed_str(value) == "") or (return_valid(value)==''):
                    continue
                st.write(f"{key}: `{fixed_str(value)}`")
            for _hearing in _hearing_df.to_dict("records"):
                _hearing_text = ''
                _hearing_text+=f"Hearing ID: `{return_valid(_hearing.pop('hearing_id'))}`"
                _hearing_text+=f", Hearing Date: `{return_valid(_hearing.pop('hearing_date'))}`"
                otext = return_valid(_hearing.pop('order_text'))
                _hearing_text+=f"Order Text: `{otext}`" if otext else ''
                pdf_link = PDFS[PDFS["pdf_id"] == _hearing["order_pdf"]]["pdf_original_website_link"].tolist()[0]
                st.page_link(pdf_link, label = _hearing_text, icon = "🔗")


# Detailed View -- Acts
def render_acts():
    acts_df = ACTSECTION.copy(deep=True)
    _act_section_id = st.columns(1)[0]
    act_section_id = _act_section_id.selectbox("ACT SECTION ID", acts_df["act_section_id"].unique().tolist())


    matter_df = MATTERS.copy(deep=True)
    _matter_df = matter_df[matter_df["act_section_id"] == act_section_id]

    if _matter_df.empty:
        st.warning("No matters found for the selected ACT SECTION ID.")
        return

    matter_ids = _matter_df["matter_id"].unique().tolist()

    # Filter hearing_df based on the matter_ids
    hearing_df = HEARINGS.copy(deep=True)
    hearing_df = hearing_df[hearing_df["matter_id"].isin(matter_ids)].copy()

    # The matter_ids used to filter the matter_df again
    matter_ids_from_hearings = hearing_df["matter_id"].unique().tolist()
    filtered_matter_df = matter_df[matter_df["matter_id"].isin(matter_ids_from_hearings)]

    # Display the filtered matters or hearings as needed
    for matter in filtered_matter_df.to_dict("records"):
        st.write(f"Matter ID: `{matter['matter_id']}`")
    
    for hearing in hearing_df.to_dict("records"):
        st.write(f"Hearing ID: `{hearing['hearing_id']}`, Hearing Date: `{hearing['hearing_date']}`")
        _matter_id = matter.pop("matter_id")
        _hearing_df = hearing_df[hearing_df["matter_id"] == _matter_id].sort_values("hearing_date")
        expander_name = ""
        expander_name += (
            f"Matter ID: `{return_valid(_matter_id)}`"
        )
        expander_name += (
            f", CNR: `{return_valid(matter.pop("cnr"))}`"
        )
        expander_name += (
            f", Filing Number: `{return_valid(matter.pop('filing_no'))}`"  
        )
        expander_name += (
            f", Filing Date: `{return_valid(matter.pop('filing_date'))}`" 
        )
        rname = return_valid(matter.pop('registration_number'))
        expander_name += (
            f", Registration Number: `{rname}`"
        ) if rname else ''
        rdate = return_valid(matter.pop('registration_date'))
        expander_name += (
            f", Registration Date: `{rdate}`"
        ) if rdate else ''

        with st.expander(expander_name):
            for key, value in matter.items():
                if key == "court_id":
                    st.write(f"Court: `{COURT[COURT["court_id"]==value]["court_name"].tolist()[0]}`")
                    continue
                if key == "act_section_id":
                    st.write(f"Act section ID: `{ACTSECTION[ACTSECTION["act_section_id"]==value]["act_name"].tolist()[0]}`")
                    continue
                if (fixed_str(value) == "") or (return_valid(value)==''):
                    continue
                st.write(f"{key}: `{fixed_str(value)}`")
            for _hearing in _hearing_df.to_dict("records"):
                _hearing_text = ''
                _hearing_text+=f"Hearing ID: `{return_valid(_hearing.pop('hearing_id'))}`"
                _hearing_text+=f", Hearing Date: `{return_valid(_hearing.pop('hearing_date'))}`"
                otext = return_valid(_hearing.pop('order_text'))
                _hearing_text+=f"Order Text: `{otext}`" if otext else ''
                pdf_link = PDFS[PDFS["pdf_id"] == _hearing["order_pdf"]]["pdf_original_website_link"].tolist()[0]
                st.page_link(pdf_link, label = _hearing_text, icon = "🔗")



def return_valid(x):
    if (
        (x is not None)
        and (x != "{}")
        and (x is not np.nan)
        and (x is not pd.NA)
        and (str(x) != "nan")
        and (x != "-")
    ):
        return x
    return ''


def fixed_str(x):
    x= str(x).replace('"', "").replace("{", "").replace("}", "").replace("\\",'') if isinstance(x,str) else x
    return x


if __name__ == "__main__":
    main()

