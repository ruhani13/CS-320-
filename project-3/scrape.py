# project: p3
# submitter: rarora23
# partner: none
# hours: 45

import os, zipfile
import time
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException

class GraphScraper:
    def __init__(self):
        self.visited = set()
        self.BFSorder = []
        self.DFSorder = []

    def go(self, node):
        raise Exception("must be overridden in sub classes -- don't change me here!")

    def dfs_search(self, node):
        if node in self.visited:
            return
        
        self.visited.add(node)
        curr_node_children = self.go(node)
        
        for child in curr_node_children:
            self.dfs_search(child)

    def bfs_search(self, node):
        todo = [node]
        self.visited.add(node)
        while(len(todo) > 0):
            curr_node = todo.pop(0)
            curr_node_children = self.go(curr_node)
            for child in curr_node_children:
                if not child in self.visited:
                    todo.append(child)
                    self.visited.add(child)
        

class FileScraper(GraphScraper):
    def __init__(self):
        super().__init__()
        if not os.path.exists("Files"):
            with zipfile.ZipFile("files.zip") as zf:
                zf.extractall()

    def go(self, node):
        if os.path.exists("Files"):
            filename = node + ".txt"
            file = os.path.join("Files", filename)
            with open(file) as f:
                lines = list(f)
                children = lines[1].strip().split(" ")
                self.BFSorder.append(lines[2].replace("BFS:", "").strip())
                self.DFSorder.append(lines[3].replace("DFS:", "").strip())
                return children
            
class WebScraper(GraphScraper):
    # required
    def __init__(self, driver=None):
        super().__init__()
        self.driver = driver
    # these three can be done as groupwork
    def go(self, url):
        self.driver.get(url)
        links = self.driver.find_elements_by_tag_name("a")
        children =  [link.get_attribute("href") for link in links]
       
        dfs_btn = self.driver.find_element_by_id("DFS")
        bfs_btn = self.driver.find_element_by_id("BFS")
        
        dfs_btn.click()
        bfs_btn.click()
        
        self.DFSorder.append(dfs_btn.text)
        self.BFSorder.append(bfs_btn.text)
        
        return children

    def dfs_pass(self, start_url):
        self.visited = set()
        self.DFSorder = []
        self.dfs_search(start_url)
        
        ret_str = ""
        for node in self.DFSorder:
            ret_str += str(node)
        return ret_str

    def bfs_pass(self, start_url):
        self.visited = set()
        self.BFSorder = []
        self.bfs_search(start_url)
        
        ret_str = ""
        for node in self.BFSorder:
            ret_str += str(node)
        return ret_str

    # write the code for this one individually
    
    def protected_df(self, url, password):        
        self.driver.get(url)
        pwd = self.driver.find_element_by_id("password-input")
        pwd.clear()
        pwd.send_keys(password)
        go = self.driver.find_element_by_id("attempt-button")
        go.click()       
        time.sleep(.2)        
        origin = self.driver.page_source
        loct = self.driver.find_element_by_id("more-locations-button")
        loct.click()  
        time.sleep(.2)
        change = self.driver.page_source
        while origin != change:
            loct = self.driver.find_element_by_id("more-locations-button")
            origin = self.driver.page_source
            loct.click()
            time.sleep(.1)
            change = self.driver.page_source
        df = pd.read_html(change)
        return df[0]
