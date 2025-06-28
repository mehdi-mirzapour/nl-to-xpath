from lxml import html

# Load HTML/XML from file
with open("resources/test_case_2.xml", "r", encoding="utf-8") as f:
    content = f.read()

# Parse content
tree = html.fromstring(content)

# Define XPath expressions to test
xpaths = {
    "All links": "//a",
    "About Us link by text": "//a[text()='About Us']",
    "About Us link by href": "//a[@href='/about-us']",
    "All buttons": "//button",
    "Visible OK buttons": "//button[text()='OK' and not(contains(@style, 'display: none'))]",
    "Hidden button": "//button[contains(@style, 'display: none')]",
    "Country dropdown": "//select[@id='country-select']",
    "Employee section header": "//section[@id='employee-section']/h2",
    "Option with value='canada'": "//option[@value='canada']",
    "Elements with data-test-id": "//*[@data-test-id]"
}

# Execute each XPath and display results
for label, xpath in xpaths.items():
    results = tree.xpath(xpath)
    print(f"\n▶ {label} ({xpath})")
    for i, r in enumerate(results, 1):
        text = r.text_content().strip() if hasattr(r, 'text_content') else str(r)
        print(f"  {i}. {text}")
