"""Browser-level Selenium tests for the prediction form.

Steps:
    1. Open application
    2. Verify page
    3. Enter valid values
    4. Trigger prediction
    5. Verify result
    6. Test invalid input
"""

import os

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

BASE_URL = os.environ.get("APP_URL", "http://localhost:5000")


@pytest.fixture(scope="module")
def driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(5)
    yield driver
    driver.quit()


def test_open_application_and_verify_page(driver):
    driver.get(BASE_URL)
    assert "ResilAI" in driver.title
    heading = driver.find_element(By.TAG_NAME, "h1")
    assert "Prediction Service" in heading.text
    status = driver.find_element(By.ID, "status")
    assert "running" in status.text


def test_valid_prediction_in_browser(driver):
    driver.get(BASE_URL)
    values = ["5.1", "3.5", "1.4", "0.2"]
    for i, value in enumerate(values):
        field = driver.find_element(By.ID, f"f{i}")
        field.clear()
        field.send_keys(value)

    driver.find_element(By.ID, "predict-btn").click()

    result = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "result"))
    )
    WebDriverWait(driver, 10).until(
        lambda d: "Prediction" in d.find_element(By.ID, "result").text
        or "Error" in d.find_element(By.ID, "result").text
    )
    assert "Prediction:" in result.text
    assert "setosa" in result.text


def test_invalid_input_in_browser(driver):
    driver.get(BASE_URL)
    driver.execute_script(
        "document.getElementById('predict-form').noValidate = true;"
    )
    driver.find_element(By.ID, "f0").clear()

    driver.find_element(By.ID, "predict-btn").click()

    result = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "result"))
    )
    WebDriverWait(driver, 10).until(
        lambda d: "Prediction" in d.find_element(By.ID, "result").text
        or "Error" in d.find_element(By.ID, "result").text
    )
    assert "Error" in result.text
