"""Script to capture UI demo screenshots using Selenium and Firefox Headless."""

import time
import os
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

OUTPUT_DIR = os.path.abspath("tailieu/images")
os.makedirs(OUTPUT_DIR, exist_ok=True)

options = Options()
options.add_argument("--headless")
options.add_argument("--window-size=1440,920")

driver = webdriver.Firefox(options=options)

try:
    print("Navigating to http://127.0.0.1:8000...")
    driver.get("http://127.0.0.1:8000")

    # 1. Wait for dashboard to populate
    WebDriverWait(driver, 10).until(
        lambda d: d.find_element(By.ID, "kpi-products").text != "0"
    )
    time.sleep(1.5)

    # Capture Dashboard (Light Mode)
    dash_path = os.path.join(OUTPUT_DIR, "demo_dashboard.png")
    driver.save_screenshot(dash_path)
    print(f"Captured: {dash_path}")

    # 2. Capture Expiring Batches Tab
    driver.find_element(By.ID, "nav-expiring").click()
    time.sleep(1.5)
    exp_path = os.path.join(OUTPUT_DIR, "demo_expiring.png")
    driver.save_screenshot(exp_path)
    print(f"Captured: {exp_path}")

    # 3. Capture POS Tab with interactive preview
    driver.find_element(By.ID, "nav-pos").click()
    time.sleep(1.0)
    try:
        prod_select = Select(driver.find_element(By.ID, "pos-product"))
        if len(prod_select.options) > 1:
            prod_select.select_by_index(1)
        qty_input = driver.find_element(By.ID, "pos-quantity")
        qty_input.clear()
        qty_input.send_keys("3")
        driver.execute_script("window.updatePOSPreview();")
        time.sleep(1.0)
    except Exception as e:
        print("POS interaction warning:", e)

    pos_path = os.path.join(OUTPUT_DIR, "demo_pos.png")
    driver.save_screenshot(pos_path)
    print(f"Captured: {pos_path}")

    # 4. Capture AI Recommendations Tab
    driver.find_element(By.ID, "nav-recommendations").click()
    time.sleep(1.5)
    rec_path = os.path.join(OUTPUT_DIR, "demo_recommendations.png")
    driver.save_screenshot(rec_path)
    print(f"Captured: {rec_path}")

    # 5. Capture Dark Mode
    driver.find_element(By.ID, "nav-dashboard").click()
    time.sleep(1.0)
    driver.execute_script("window.toggleTheme();")
    time.sleep(1.0)
    dark_path = os.path.join(OUTPUT_DIR, "demo_dark_mode.png")
    driver.save_screenshot(dark_path)
    print(f"Captured: {dark_path}")

    print("All screenshots successfully captured!")

finally:
    driver.quit()
