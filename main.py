import os
from dotenv import load_dotenv
import streamlit as st
import matplotlib.pyplot as plt
from google.oauth2 import service_account
from google.cloud import bigquery
import plotly.express as px
import google.auth
from google.auth import compute_engine

load_dotenv()

project_id = os.getenv("PROJECT_ID")
credentials_path = os.getenv("CREDENTIALS_PATH")

try:
    # Local에 저장된 json 파일 불러오기
    credentials = service_account.Credentials.from_service_account_file(
        credentials_path
    )
except:
    credentials, project_id = google.auth.default()
    print(f"credentials.service_account_email: {credentials.service_account_email}")
    credentials = compute_engine.Credentials(
        service_account_email=credentials.service_account_email,
    )

# GCP 프로젝트
client = bigquery.Client(credentials=credentials, project=project_id)

print("BigQuery 클라이언트가 성공적으로 생성되었습니다.")


@st.cache_data(ttl=600)
def getData(query):
    data = client.query(query).to_dataframe()
    int64_columns = data.select_dtypes(include=["int64"]).columns
    data[int64_columns] = data[int64_columns].astype("float64")
    print(data.info())
    return data


def plotly_chart(data, feature):
    main_features = ["LotArea", "GrLivArea", "SalePrice"]
    chart_features = main_features + [feature]
    DF = data[chart_features]

    # .......main plot(scatter)
    fig = px.scatter(
        DF,
        x="GrLivArea",
        y="SalePrice",
        color=feature,
        size="LotArea",
        width=750,
        height=400,
    )

    # .......annotation (text)
    fig.add_annotation(
        text="Possible outliers",
        xref="x",
        yref="y",
        x=6200,
        y=160000,
        showarrow=True,
        xshift=-60,
        yshift=30,
        font=dict(family="sans serif", size=12, color="LightSeaGreen"),
    )

    # .......annotation (box)
    fig.add_shape(
        type="rect",
        x0=4500,
        y0=100000,
        x1=5800,
        y1=250000,
        fillcolor="lightgray",
        line_color="black",
        opacity=0.3,
    )

    # .......update the plot as you wish
    fig.update_layout(
        title="<b>House Price vs GrLivArea<b>",
        titlefont={"size": 24},
    )

    st.plotly_chart(fig)


def main():
    st.header("Keyper", divider="rainbow")

    # st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown(
        """
                <style>
                .gcp-font {
                    font-size: 32px !important;
                }
                </style>
                """,
        unsafe_allow_html=True,
    )

    st.markdown(
        "<p class='gcp-font'>BigQuery with Streamlit</p>", unsafe_allow_html=True
    )

    query = f"""
        SELECT *
          FROM `{project_id}.kaggle.transformed_train`
    """

    data = getData(query)
    st.dataframe(data.head(3))

    object_features = st.selectbox(
        "Select....", ("OverallQual", "ExterQual", "RoofStyle"), index=0
    )
    plotly_chart(data, object_features)

    st.markdown(
        "<p class='gcp-font'>BigQuery with Streamlit in GCP</p>", unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
