```python
from pathlib import Path
import pandas as pd
import streamlit as st
import re


# ==================================================
# CSV 파일 경로
# ==================================================

BASE_DIR = Path(__file__).resolve().parent

CSV_FILENAME = "전국통합식품영양성분정보표준데이터.csv"

# 기존 경로 유지
CSV_PATH = BASE_DIR / "data" / CSV_FILENAME


def find_food_csv():
    """프로젝트 내부에서 식품 영양성분 CSV 파일을 찾는다."""

    search_roots = [
        BASE_DIR,
        BASE_DIR.parent
    ]

    found_files = []

    for root in search_roots:
        if not root.exists():
            continue

        for path in root.rglob("*"):
            if not path.is_file():
                continue

            # Git 및 가상환경 폴더 제외
            if any(
                part in {".git", ".venv", "venv", "__pycache__"}
                for part in path.parts
            ):
                continue

            if path.suffix.lower() == ".csv":
                found_files.append(path)

    # 중복 경로 제거
    found_files = list(dict.fromkeys(found_files))

    # 파일명이 정확히 일치하는 경우 우선 사용
    exact_matches = [
        path for path in found_files
        if path.name == CSV_FILENAME
    ]

    if exact_matches:
        return exact_matches[0]

    # 식품 또는 영양이 포함된 파일명 검색
    matching_files = [
        path for path in found_files
        if "식품" in path.name or "영양" in path.name
    ]

    if len(matching_files) == 1:
        return matching_files[0]

    # 프로젝트 내부 CSV가 하나뿐이라면 해당 파일 사용
    if len(found_files) == 1:
        return found_files[0]

    if len(matching_files) > 1 or len(found_files) > 1:
        raise FileNotFoundError(
            "사용할 식품 데이터 CSV 파일을 하나로 결정할 수 없습니다.\n"
            "발견된 CSV 파일:\n"
            + "\n".join(str(path) for path in found_files)
        )

    raise FileNotFoundError(
        "식품 데이터 CSV 파일을 찾을 수 없습니다.\n"
        f"기본 확인 경로: {CSV_PATH}\n"
        f"검색한 프로젝트 경로: {BASE_DIR}"
    )


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
    """빈칸이나 숫자가 아닌 값을 안전하게 처리한다."""

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
# 식품 데이터 불러오기
# ==================================================

@st.cache_data
def load_food_database():

    # CSV 파일 자동 검색
    csv_path = find_food_csv()

    encodings = [
        "utf-8-sig",
        "cp949",
        "euc-kr",
        "utf-8"
    ]

    df = None
    last_error = None

    # 인코딩을 바꾸어 가며 CSV 읽기
    for encoding in encodings:
        try:
            df = pd.read_csv(
                csv_path,
                encoding=encoding,
                low_memory=False
            )
            break

        except UnicodeDecodeError as error:
            last_error = error

    if df is None:
        raise ValueError(
            "CSV 인코딩을 확인할 수 없습니다.\n"
            f"파일 경로: {csv_path}\n"
            f"오류 내용: {last_error}"
        )

    # 열 이름 앞뒤 공백 제거
    df.columns = df.columns.astype(str).str.strip()

    # 필수 열 확인
    required_columns = [
        "식품명",
        "데이터구분명",
        "영양성분함량기준량"
    ]

    missing = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing:
        raise ValueError(
            "CSV에 필요한 열이 없습니다.\n"
            f"누락된 열: {missing}\n"
            f"실제 CSV 열 이름: {df.columns.tolist()}"
        )

    # 음식 데이터만 사용
    df["데이터구분명"] = (
        df["데이터구분명"]
        .astype(str)
        .str.strip()
    )

    df = df[
        df["데이터구분명"].eq("음식")
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

    # 기준량 정리
    df["기준단위"] = (
        df["영양성분함량기준량"]
        .astype(str)
        .str.strip()
        .str.replace(" ", "", regex=False)
    )

    # 100g / 100ml 기준 데이터만 사용
    df = df[
        df["기준단위"].isin(["100g", "100ml"])
    ].copy()

    if df.empty:
        raise ValueError(
            "음식 데이터가 없거나 100g, 100ml 기준 자료를 찾을 수 없습니다.\n"
            "CSV의 데이터구분명과 영양성분함량기준량을 확인해 주세요."
        )

    # 기준값 숫자 변환
    df["기준값"] = df["기준단위"].str.extract(
        r"(\d+(?:\.\d+)?)"
    )[0]

    df["기준값"] = pd.to_numeric(
        df["기준값"],
        errors="coerce"
    )

    # 영양소 열 숫자 변환
    for key, column in NUTRIENT_COLUMNS.items():

        if column in df.columns:
            df[column] = pd.to_numeric(
                df[column]
                .astype(str)
                .str.replace(",", "", regex=False)
                .str.strip(),
                errors="coerce"
            )

        else:
            # CSV에 해당 영양소 열이 없으면 결측값으로 처리
            df[column] = None

    # 100g 기준 자료를 우선 사용
    df["단위우선순위"] = (
        df["기준단위"]
        .map({"100g": 0, "100ml": 1})
    )

    df = df.sort_values(
        ["식품명", "단위우선순위"]
    )

    # 동일 식품명 중복 제거
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
# 식품 영양 정보
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
        "basis_value": to_number(row["기준값"]),
    }

    for key, column in NUTRIENT_COLUMNS.items():

        if column in df.columns:
            info[key] = to_number(row[column])
        else:
            info[key] = None

    return info


# ==================================================
# 섭취량에 따른 영양소 계산
# ==================================================

def calculate_nutrients(food_name, amount):

    info = get_food_info(food_name)

    if info is None:
        return None

    amount = to_number(amount)
    basis_value = info["basis_value"]

    if amount <= 0 or basis_value <= 0:
        return None

    # 기준량에 따른 섭취 비율 계산
    multiplier = amount / basis_value

    result = {
        "name": info["name"],
        "amount": amount,
        "unit": "g" if info["basis"] == "100g" else "ml",
        "basis": info["basis"],
    }

    for key in NUTRIENT_COLUMNS:

        value = info.get(key)

        if value is None:
            result[key] = None
        else:
            result[key] = value * multiplier

    return result


# ==================================================
# 여러 식품의 영양소 합계
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
```
