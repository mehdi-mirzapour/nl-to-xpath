from lxml import etree

instructions = [
    {
        "nl": "Click on 'about us'",
        "xpath": "//a[normalize-space(text())='About Us']"
    },
    {
        "nl": "Hover over 'ok' under 'Employee' section",
        "xpath": (
            "//section[@id='employee-section']"
            "//div[contains(@class, 'employee')]"
            "//button[normalize-space(text())='OK']"
        )
    },
    {
        "nl": "Select the dropdown next to 'Country'",
        "xpath": "//label[normalize-space(text())='Country:']/following-sibling::select"
    }
]

# Path to your external HTML file
html_file_path = "resources/test_case_1.html"

# Read HTML from file
with open(html_file_path, 'r', encoding='utf-8') as f:
    html_content = f.read()

# Parse the HTML string into an lxml etree object
dom = etree.HTML(html_content)

def describe_element(elem):
    tag = elem.tag
    text = (elem.text or "").strip()
    attrib = {k: v for k, v in elem.attrib.items()}
    return f"<{tag} {attrib}> text='{text}'"

for entry in instructions:
    nl = entry["nl"]
    xpath = entry["xpath"]
    elements = dom.xpath(xpath)

    print(f"Instruction: {nl}")
    print(f"XPath: {xpath}")
    if not elements:
        print("  → No elements matched the XPath.\n")
        continue
    
    for i, el in enumerate(elements, 1):
        print(f"  Match {i}: {describe_element(el)}")
    print()
