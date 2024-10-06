import datetime as dt

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

ACTSECTION = pd.read_csv("data/actsection.csv")
COURT = pd.read_csv("data/court.csv")
HEARINGS = pd.read_csv("data/hearings.csv")
HEARINGS["hearing_date"] = pd.to_datetime(HEARINGS["hearing_date"])
JUDGE = pd.read_csv("data/judge.csv")
MATTERS = pd.read_csv("data/matters.csv")
MATTERS["filing_date"] = pd.to_datetime(MATTERS["filing_date"])
PDFS = pd.read_csv("data/pdfs.csv")

st.set_page_config(layout="wide")


def main():
    st.sidebar.title("Legal Data")
    view = st.sidebar.radio("View", options=[ "Detail","Overview"])
    if view == "Overview":
        render_overview()
    if view == "Detail":
        render_detail()


def render_overview():
    judge_plot = overview_judge_plot()
    st.plotly_chart(judge_plot,use_container_width = True)
    status_plot, typology_plot,act_plot = overview_case_type_plot()
    _status_plot, _typology_plot,_act_plot = st.columns(3)
    _status_plot.plotly_chart(status_plot,use_container_width = True)
    _typology_plot.plotly_chart(typology_plot,use_container_width = True)
    _act_plot.plotly_chart(act_plot,use_container_width = True)
    

def overview_judge_plot():
    hearing_df = HEARINGS.copy(deep=True)[["judge_id", "matter_id", "hearing_id"]]
    judge_df = JUDGE.copy(deep = True)[["judge_id", "judge_name"]]
    df = hearing_df.merge(judge_df).groupby("judge_name")[["hearing_id"]].count().sort_values("hearing_id").reset_index().rename(columns = {"hearing_id":"Hearings", "judge_name":"Judge"})
    fig = px.bar(df, y = "Judge", x = "Hearings", title = "Hearings per Judge")
    return fig


def overview_case_type_plot():
    matter_df = MATTERS.copy(deep=True)
    act_df =ACTSECTION.copy(deep=True)
    status_df = matter_df.groupby("case_status")["matter_id"].count().reset_index().rename(columns = {"case_status":"Case Status", "matter_id": "Count"})
    typology_df = matter_df.groupby("case_typology")["matter_id"].count().reset_index().rename(columns = {"case_typology":"Case Typology", "matter_id": "Count"})
    status_fig = px.pie(status_df, values = "Count", names = "Case Status",color_discrete_sequence=px.colors.sequential.RdBu, title = "Distribution of Case Status")
    typology_fig = px.pie(typology_df, values = "Count", names = "Case Typology",color_discrete_sequence=px.colors.sequential.RdBu,title = "Distribution of Case Typology")
    act_section = matter_df[["act_section_id"]].merge(act_df).dropna(subset = ["act_name"]).groupby("act_name")[["act_section_id"]].count().reset_index().rename(columns = {"act_name":"Act Name", "act_section_id": "Count"})
    act_fig = px.pie(act_section, values = "Count", names = "Act Name",color_discrete_sequence=px.colors.sequential.RdBu, title = "Distribution of Acts")
    return status_fig,typology_fig,act_fig
    

def render_detail():
    detail_for = st.sidebar.radio("Feature",["Judge", "Matter", "Acts"])
    if detail_for == "Judge":
        render_judge()
    if detail_for == "Matter":
        render_matter()
    if detail_for == "Acts":
        render_acts()

# Detailed View -- Judge
def render_judge():
    judge_df = JUDGE.copy(deep=True)
    _judge_name, _case_status, _case_typology = st.columns([3, 2, 2])
    judge_name = _judge_name.selectbox(
        "Judge Name", judge_df["judge_name"].dropna().unique().tolist()
    )

    matter_df = MATTERS.copy(deep=True)
    hearing_df = HEARINGS.copy(deep=True)
    judge_id = judge_df[judge_df["judge_name"] == judge_name]["judge_id"].tolist()
    if not len(judge_id) == 1:
        st.warning("Multiple ids for same judge")
        st.stop()
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
    _render_matter(matter_df,hearing_df)
    

# Detailed view -- Matter
def render_matter():
    filter_by = st.sidebar.radio("Filter By", ["Case Type", "Filing Date", "Petitioners"])
    if filter_by == "Case Type":
        render_matter_case_type()
    elif filter_by == "Filing Date":
        render_matter_filing_date()
    elif filter_by == "Petitioners":
        render_matter_petitioners()

    

def render_matter_filing_date():
    matter_df = MATTERS.copy(deep=True).sort_values("filing_date")
    min_date = matter_df["filing_date"].min()
    max_date = matter_df["filing_date"].max()
    _date, _ = st.columns([3,7])
    d = _date.date_input("Filing Date", (min_date,max_date),min_date,max_date)
    if len(d) !=2:
        st.stop()
    start,end = d
    start = dt.datetime.combine(start, dt.time(0,0))
    end = dt.datetime.combine(end, dt.time(0,0))
    matter_df = matter_df[(matter_df["filing_date"]>= start) & (matter_df["filing_date"] <= end)]
    if matter_df.empty:
        st.info("No matters were filed in this time period. Choose a different time frame.")
    hearing_df = HEARINGS.copy(deep=True)
    hearing_df = hearing_df[hearing_df["matter_id"].isin(matter_df["matter_id"].tolist())]
    _render_matter(matter_df,hearing_df)


def render_matter_petitioners():
    matter_df = MATTERS.copy(deep=True).sort_values("filing_date")
    matter_df["petitioners"] = matter_df["petitioners"].apply(lambda x: fixed_str(x))
    _petitioner,_ = st.columns([6,3])
    petitioner = _petitioner.selectbox("Petitioner", matter_df["petitioners"].unique())
    matter_df = matter_df[matter_df["petitioners"]==petitioner]
    hearing_df = HEARINGS.copy(deep=True)
    hearing_df = hearing_df[hearing_df["matter_id"].isin(matter_df["matter_id"].tolist())]
    _render_matter(matter_df,hearing_df)


def render_matter_case_type():
    matter_df = MATTERS.copy(deep=True)
    _case_typology, _is_disposed, _disposed_or_status,_ = st.columns([3,3,3,2])
    case_typology = _case_typology.selectbox("Case Typology", matter_df["case_typology"].unique())
    matter_df = matter_df[matter_df["case_typology"] == case_typology]
    is_disposed = _is_disposed.checkbox("Case Disposed", True)
    if is_disposed:
        matter_df = matter_df[matter_df["case_status"]=="Disposed"]
        disposed_or_status = _disposed_or_status.multiselect("Disposal Type", matter_df["disposal_type"].unique())
        if not disposed_or_status:
            st.info("Choose Disposal Type")
            st.stop()
        matter_df = matter_df[matter_df["disposal_type"].isin(disposed_or_status)]
    else:
        matter_df = matter_df[matter_df["case_status"]!="Disposed"]
    hearing_df = HEARINGS.copy(deep=True)
    hearing_df = hearing_df[hearing_df["matter_id"].isin(matter_df["matter_id"].tolist())]
    _render_matter(matter_df,hearing_df)

    
def _render_matter(matter_df, hearing_df):    
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
                _hearing_text+=f", Hearing Date: `{str(return_valid(_hearing.pop('hearing_date')))[:10]}`"
                otext = return_valid(_hearing.pop('order_text'))
                _hearing_text+=f"Order Text: `{otext}`" if otext else ''
                pdf_link = PDFS[PDFS["pdf_id"] == _hearing["order_pdf"]]["pdf_original_website_link"].tolist()[0]
                st.page_link(pdf_link, label = _hearing_text, icon = "🔗")



# Detailed View -- Acts
def render_acts():
    matter_df = MATTERS.copy(deep=True)
    act_ids = matter_df["act_section_id"].dropna().unique().tolist()
    act_df = ACTSECTION.copy(deep=True)
    act_df = act_df[act_df["act_section_id"].isin(act_ids)]
    act_name_list = act_df["act_name"].dropna().unique().tolist() # FIXME no dropna
    _act_name, _ = st.columns([3,7])
    act_name = _act_name.selectbox("Act Name", act_name_list)
    act_section_ids = act_df[act_df["act_name"]==act_name]["act_section_id"].dropna().unique().tolist()
    matter_df = matter_df[matter_df["act_section_id"].isin(act_section_ids)]
    hearing_df = HEARINGS.copy(deep=True)
    hearing_df = hearing_df[hearing_df["matter_id"].isin(matter_df["matter_id"].tolist())]
    _render_matter(matter_df,hearing_df)


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
