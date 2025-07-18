from backend.backend_tools.web_scrapping.driver import Driver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class xingDriver(Driver):
    def __init__(self):
        options = Options()
        #options.add_argument(r"--user-data-dir=C:\Users\umutc\chrome_selenium_profile")
        #options.add_argument("--profile-directory=Default")
        #options.add_argument("--no-sandbox")
        #options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--log-level=3")  # only fatal errors
        super().__init__(options=options)

    def getJobContents(self, url):
        self.getURL(url)
        wait = WebDriverWait(self.driver, 10)

        # Try clicking "Show more" up to 3 times
        for _ in range(3):
            try:
                show_more_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Show more']")))
                show_more_btn.click()
            except:
                print("No 'Show more' button found or it is not clickable — continuing.")
                break

        # Wait for job cards to load
        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.card-styles__CardLink-sc-ecfcdbce-2.eVLJBS")))
        job_links = self.driver.find_elements(By.CSS_SELECTOR, "a.card-styles__CardLink-sc-ecfcdbce-2.eVLJBS")

        # Extract job titles and hrefs
        job_info_list = []
        for link in job_links:
            title = link.get_attribute("aria-label") or link.text.strip()
            href = link.get_attribute("href")
            if href:
                job_info_list.append({"title": title, "url": href})

        results = []
        main_window = self.driver.current_window_handle

        for job in job_info_list:
            # Open in new tab
            self.driver.execute_script(f"window.open('{job['url']}', '_blank');")
            WebDriverWait(self.driver, 10).until(lambda d: len(d.window_handles) > 1)

            # Switch to the new tab
            new_tab = [h for h in self.driver.window_handles if h != main_window][0]
            self.driver.switch_to.window(new_tab)

            # Scrape job content
            body = self.get_job_body()
            print(f"Scraped content for {job['title']}: {body[:100]}...")
            results.append({
                "title": job["title"],
                "url": job["url"],
                "content": body
            })

            # Close new tab and return to main window
            self.driver.close()
            self.driver.switch_to.window(main_window)

        # Close main window
        self.driver.close()

        #print(results)
        return results
