import time
import os
from selenium.webdriver import Firefox, FirefoxOptions


TRANZILA_LOGIN = ""
TRANZILA_PWD = ""
TRANZILA_TIMEOUT = 10


MY_SITE_LOGIN = ""
MY_SITE_PWD = ""

last_transaction_id = 0


def get_last_transaction_id():
	global last_transaction_id
	with open("last_transaction.txt", "r") as f:
		try:
			last_transaction_id = int(f.read())
		except:
			last_transaction_id = 0


def write_last_transaction_id(last_id):
	with open("last_transaction.txt", "w") as f:
		f.write(str(last_id))


def tranzila_login():
	driver.get("https://my.tranzila.com/login")
	driver.find_element_by_id("login_name").send_keys(TRANZILA_LOGIN)
	driver.find_element_by_id("login_password").send_keys(TRANZILA_PWD)
	driver.find_element_by_id("remember_me").click()
	driver.find_element_by_css_selector("button[type='submit']").click()


def my_site_login():
	url = "https://www.7-40.pro/admin.php?admin"
	driver.execute_script(f"window.open('{url}', '_blank');")
	driver.switch_to.window(driver.window_handles[1])
	time.sleep(10)
	driver.find_element_by_name("apass").send_keys(MY_SITE_PWD)
	driver.find_element_by_name("submit").click()


def tranzila_get_deals():
	global last_transaction_id
	driver.switch_to.window(driver.window_handles[0])
	url = "https://my.tranzila.com/transactions/txns_list"
	driver.get(url)
	time.sleep(10)
	trs = driver.find_elements_by_css_selector("div#TableView table.k-selectable tbody tr")
	if len(trs) == 0:
		print("Сделок за сегодня не обнаружено!")
	else:
		for tr in trs:
			index = int(tr.find_element_by_css_selector("td[data-field='INDEX']").text)
			if index > last_transaction_id:
				tr.find_element_by_css_selector("td[data-field='INDEX']").click()
				time.sleep(10)
				frame = driver.find_element_by_css_selector("iframe.k-content-frame")
				driver.switch_to.frame(frame)
				xpath = "(//div[@class='deal_info_inner']//span[contains(text(), 'סטטוס')])[1]/../../div[@class='value_wrap']/span"
				tmp = driver.find_element_by_xpath(xpath).text
				if tmp != "מאושר":
					driver.switch_to.default_content()
					driver.execute_script("""document.querySelector("a[aria-label='Close']").click()""")
					time.sleep(2)
					continue
				xpath = "(//div[@class='deal_info_inner']//span[contains(text(), 'סוג עסקה')])[1]/../../div[@class='value_wrap']/span"
				tmp = driver.find_element_by_xpath(xpath).text
				if tmp != "חיוב":
					driver.switch_to.default_content()
					driver.execute_script("""document.querySelector("a[aria-label='Close']").click()""")
					time.sleep(2)
					continue
				xpath = "(//div[@class='deal_info_inner']//span[contains(text(), 'סכום')])[1]/../../div[@class='value_wrap']/span"
				deal_sum = float(driver.find_element_by_xpath(xpath).text.strip("₪ "))
				xpath = "(//span[contains(text(), 'אימייל')])[1]/../../div[@class='value_wrap']/span"
				deal_email = driver.find_element_by_xpath(xpath).text
				add_money(deal_email, deal_sum)
				driver.switch_to.window(driver.window_handles[0])
				last_transaction_id = index
				driver.switch_to.default_content()
				driver.execute_script("""document.querySelector("a[aria-label='Close']").click()""")
				time.sleep(2)
		write_last_transaction_id(last_transaction_id)
		

def add_money(email, money):
	driver.switch_to.window(driver.window_handles[1])
	url = "https://www.7-40.pro/adminda.php"
	driver.get(url)
	xpath = f"(//a[contains(text(), '{email}')]/../../../tr)[4]//a[contains(@href, 'adminpay.php')]"
	element = driver.find_element_by_xpath(xpath)
	if element:
		element.click()
		time.sleep(5)
		element = driver.find_element_by_name("pay")
		val = element.get_attribute("value")
		try:
			val = int(val)
		except:
			val = float(val)
		val += money
		driver.execute_script("""document.querySelector("input[name='pay']").setAttribute("value", "")""")
		element.send_keys(str(val))
		driver.find_element_by_css_selector("input[type='submit']").click()
		print(f"На счет {email} успешно добавлено {money}")
	else:
		print(f"Не удалось обнаружить {email}")


def run():
	get_last_transaction_id()
	tranzila_login()
	my_site_login()
	while True:
		try:
			tranzila_get_deals()
		except Exception as e:
			print("Не удалось получить данные о сделках: ", e)
		time.sleep(2 * 60)


try:
	opts = FirefoxOptions()
	opts.headless = True
	opts.binary_location = "C:\Program Files\Mozilla Firefox\firefox.exe"
	driver = Firefox(options=opts)
	run()
except Exception as e:
	print("Ошибка! Аварийное завершение работы")
	print(e)
finally:
	driver.quit()
	print("Завершение работы")
