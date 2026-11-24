# ===== 1. 라이브러리 불러오기 =====
import streamlit as st
import pandas as pd
import plotly.express as px

# [추가] 가장 먼저 실행되는 Streamlit 설정 명령
st.set_page_config(page_title="Titanic 대시보드", layout="wide")

# ===== 2. 데이터 로드 함수 =====
# st.cache_data를 사용하여 titanic.csv를 처음 한 번만 읽고 캐싱
@st.cache_data
def load_data():
    return pd.read_csv("titanic.csv")

# ===== 3. 데이터 필터링 및 분석 함수 =====
# 조건에 맞는 승객 데이터만 걸러내는 함수
def filter_data(df, sexes, classes, age_range):
    min_age, max_age = age_range
    cond_sex = df["sex"].isin(sexes)
    cond_class = df["pclass"].isin(classes)
    cond_age = df["age"].between(min_age, max_age)
    return df[cond_sex & cond_class & cond_age]

# 대시보드 상단 KPI(승객 수, 생존율, 평균 나이) 계산 함수
def kpi(df):
    if df.empty:
        return 0, 0, 0
    total_passengers = len(df)
    survival_rate = round(df["survived"].mean() * 100, 1)
    mean_age_val = df["age"].mean()
    avg_age = 0.0 if pd.isna(mean_age_val) else round(mean_age_val, 1)
    return total_passengers, survival_rate, avg_age

# ===== 4. 시각화 차트 생성 함수 =====
# 객실 등급별 생존율(%) 막대 그래프 함수
def class_rate_bar(df):
    rate_df = df.groupby("pclass", as_index=False)["survived"].mean()
    rate_df["survival_rate"] = (rate_df["survived"] * 100).round(1)
    fig = px.bar(
        rate_df,
        x="pclass",
        y="survival_rate",
        text_auto=True,
        title="객실 등급별 생존율 (%)",
        labels={"pclass": "객실 등급", "survival_rate": "생존율 (%)"}
    )
    fig.update_traces(textposition="outside")
    fig.update_xaxes(type="category")
    return fig

# 생존 여부별 나이 히스토그램 함수
def age_hist(df):
    fig = px.histogram(
        df,
        x="age",
        color="survived",
        barmode="overlay",
        opacity=0.6,
        title="생존 여부별 승객 나이 분포",
        labels={"age": "나이", "survived": "생존 여부 (0: 사망, 1: 생존)"}
    )
    return fig

# ===== 5. 페이지 제목 및 데이터 로드 =====
# (상단으로 이동된 st.set_page_config 제거 후 제목 출력)
st.title("타이타닉, 누가 살아남았나?")

# 캐싱된 데이터 불러오기
df = load_data()

# ===== 6. 사이드바 필터 구성 =====
st.sidebar.header("검색 조건 필터")

# 성별 다중 선택 (기본값: 전체 선택)
sex_options = ["male", "female"]
selected_sexes = st.sidebar.multiselect("성별 선택", options=sex_options, default=sex_options)

# 객실 등급 다중 선택 (기본값: 1, 2, 3등급 모두 선택)
class_options = [1, 2, 3]
selected_classes = st.sidebar.multiselect("객실 등급 선택", options=class_options, default=class_options)

# 나이 범위 슬라이더 (0 ~ 80세)
selected_age_range = st.sidebar.slider("나이 범위 선택", min_value=0, max_value=80, value=(0, 80))

# ===== 7. 본문 출력 =====
# 사이드바에서 선택한 조건으로 데이터 필터링 실행
filtered_df = filter_data(df, selected_sexes, selected_classes, selected_age_range)

# kpi 함수로 승객 수, 생존율, 평균 나이 계산
total_passengers, survival_rate, avg_age = kpi(filtered_df)

# st.columns(3)으로 3칸 레이아웃 생성 후 KPI 숫자 카드 표시
col1, col2, col3 = st.columns(3)
col1.metric("승객 수", f"{total_passengers}명")
col2.metric("생존율", f"{survival_rate}%")
col3.metric("평균 나이", f"{avg_age}세")

# [추가] KPI 아래 st.columns(2)로 좌우 2칸 분할하여 차트 2개 배치
chart_col1, chart_col2 = st.columns(2)

# [추가] 왼쪽 칸에 객실 등급별 생존율 막대 그래프 표시
with chart_col1:
    st.plotly_chart(class_rate_bar(filtered_df), use_container_width=True)

# [추가] 오른쪽 칸에 생존 여부별 나이 히스토그램 표시
with chart_col2:
    st.plotly_chart(age_hist(filtered_df), use_container_width=True)

# [추가] 맨 아래 접기(expander) 안에 필터링된 데이터프레임 표 출력
with st.expander("데이터 보기"):
    st.dataframe(filtered_df, use_container_width=True)
