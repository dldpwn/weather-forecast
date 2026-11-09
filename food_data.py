
from pathlib import Path
import unicodedata
import re

import pandas as pd
import streamlit as st


# ==================================================
# CSV 파일 경로 설정
# ==================================================

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

EXPECTED_FILENAME = "전국통합식품영양성분정보표준데이터.csv"


def find_food_csv():

    if not DATA_DIR.exists():
        raise FileNotFoundError(
            f"식품 데이터 폴더를 찾을 수 없습니다: {DATA_DIR}"
        )

    expected_name = unicodedata.normalize(
        "NFC",
        EXPECTED_FILENAME
    )

    for file_path in DATA_DIR.iterdir():

        if not file_path.is_file():
            continue

        actual_name = unicodedata.normalize(
            "NFC",
            file_path.name
        )

        if actual_name == expected_name:
            return file_path

    csv_files = [
        file.name
        for file in DATA_DIR.iterdir()
        if file.is_file() and file.suffix.lower() == ".csv"
    ]

    raise FileNotFoundError(
        "식품 데이터 파일을 찾을 수 없습니다.\n"
        f"확인한 폴더: {DATA_DIR}\n"
        f"폴더 안의 CSV 파일: {csv_files}"
    )


CSV_PATH = find_food_csv()


# ==================================================
# 영양소 열 이름
# ==================================================

NUTRIENT_COLUMNS = {
    "kcal": "에너지(kcal)",
    "water": "수분(g)",
    "protein": "단백질(g)",
    "fat": "지방(g)",
    "carbs": "탄수화물(g)",
    "sugar": "당류(g)",
    "fiber": "식이섬유(g)",
    "calcium": "칼슘(mg)",
    "iron": "철(mg)",
    "phosphorus": "인(mg)",
    "potassium": "칼륨(mg)",
    "sodium": "나트륨(mg)",
    "vitamin_a": "비타민 A(μg RAE)",
    "vitamin_b1": "티아민(mg)",
    "vitamin_b2": "리보플라빈(mg)",
    "niacin": "니아신(mg)",
    "vitamin_c": "비타민 C(mg)",
    "vitamin_d": "비타민 D(μg)",
    "cholesterol": "콜레스테롤(mg)",
    "saturated_fat": "포화지방산(g)",
    "trans_fat": "트랜스지방산(g)",
}


# ==================================================
# 숫자 변환
# ==================================================

def to_number(value):

    if pd.isna(value):
        return 0.0

    try:
        value = str(value).replace(",", "").strip()

        if value == "":
            return 0.0

        return float(value)

    except (ValueError, TypeError):
        return 0.0


# ==================================================
# 식품 데이터베이스 불러오기
# ==================================================

@st.cache_data
def load_food_database():

    if not CSV_PATH.exists():
        raise FileNotFoundError(
            f"식품 데이터 파일이 없습니다: {CSV_PATH}"
        )

    encodings = [
        "utf-8-sig",
        "cp949",
        "euc-kr",
        "utf-8"
    ]

    df = None
    last_error = None

    for encoding in encodings:

        try:
            df = pd.read_csv(
                CSV_PATH,
                encoding=encoding,
                low_memory=False
            )
            break

        except UnicodeDecodeError as error:
            last_error = error

    if df is None:
        raise ValueError(
            "CSV 파일의 문자 인코딩을 확인할 수 없습니다."
        ) from last_error

    # 필수 열 확인
    required_columns = [
        "식품명",
        "데이터구분명",
        "영양성분함량기준량"
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            "CSV 파일에 필요한 열이 없습니다: "
            + ", ".join(missing_columns)
        )

    # 음식 데이터만 사용
    df = df[
        df["데이터구분명"]
        .astype(str)
        .str.strip()
        .eq("음식")
    ].copy()

    # 식품명 정리
    df["식품명"] = (
        df["식품명"]
        .astype(str)
        .str.strip()
    )

    df = df[
        df["식품명"].ne("")
        & df["식품명"].ne("nan")
    ].copy()

    # 영양소 열이 없는 경우 0으로 처리
    for column in NUTRIENT_COLUMNS.values():

        if column in df.columns:
            df[column] = df[column].apply(to_number)

        else:
            df[column] = 0.0

    # 기준량 정리
    df["기준단위"] = (
        df["영양성분함량기준량"]
        .astype(str)
        .str.strip()
    )

    df["기준값"] = df["기준단위"].str.extract(
        r"(\d+(?:\.\d+)?)"
    )[0]

    df["기준값"] = pd.to_numeric(
        df["기준값"],
        errors="coerce"
    )

    # 100g 또는 100ml 기준 데이터만 사용
    df = df[
        df["기준단위"].isin(["100g", "100ml"])
    ].copy()

    # 같은 식품명이 여러 개면 100g 기준 우선
    df["단위우선순위"] = (
        df["기준단위"]
        .map({
            "100g": 0,
            "100ml": 1
        })
    )

    df = df.sort_values(
        ["식품명", "단위우선순위"]
    )

    df = df.drop_duplicates(
        subset=["식품명"],
        keep="first"
    )

    return df.reset_index(drop=True)


# ==================================================
# 식품명 목록
# ==================================================

def get_food_names():

    df = load_food_database()

    return sorted(
        df["식품명"]
        .dropna()
        .unique()
        .tolist()
    )


# ==================================================
# 식품 검색
# ==================================================

def search_food(keyword, limit=30):

    df = load_food_database()

    keyword = str(keyword).strip()

    if not keyword:
        return df.head(limit)

    result = df[
        df["식품명"].str.contains(
            re.escape(keyword),
            case=False,
            na=False
        )
    ]

    return result.head(limit)


# ==================================================
# 식품 영양 정보 조회
# ==================================================

def get_food_info(food_name):

    df = load_food_database()

    result = df[
        df["식품명"] == food_name
    ]

    if result.empty:
        return None

    row = result.iloc[0]

    info = {
        "name": row["식품명"],
        "basis": row["기준단위"],
        "basis_value": to_number(row["기준값"])
    }

    for key, column in NUTRIENT_COLUMNS.items():

        if column in df.columns:
            info[key] = to_number(row[column])

        else:
            info[key] = None

    return info


# ==================================================
# 실제 섭취량 기준 영양소 계산
# ==================================================

def calculate_nutrients(food_name, amount):

    info = get_food_info(food_name)

    if info is None:
        return None

    amount = to_number(amount)

    basis_value = info["basis_value"]

    if amount <= 0 or basis_value <= 0:
        return None

    multiplier = amount / basis_value

    result = {
        "name": info["name"],
        "amount": amount,
        "unit": (
            "g"
            if info["basis"] == "100g"
            else "ml"
        ),
        "basis": info["basis"]
    }

    for key in NUTRIENT_COLUMNS:

        value = info.get(key)

        if value is None:
            result[key] = None

        else:
            result[key] = value * multiplier

    return result


# ==================================================
# 여러 음식의 영양소 합계 계산
# ==================================================

def calculate_total_nutrients(food_records):

    totals = {
        key: 0.0
        for key in NUTRIENT_COLUMNS
    }

    valid_count = 0

    for record in food_records:

        food_name = record.get("food_name")
        amount = record.get("amount", 0)

        if not food_name:
            continue

        nutrients = calculate_nutrients(
            food_name,
            amount
        )

        if nutrients is None:
            continue

        for key in totals:

            value = nutrients.get(key)

            if value is not None:
                totals[key] += value

        valid_count += 1

    return totals, valid_count
