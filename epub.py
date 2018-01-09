import os
import shutil
import sys
import tempfile
import xml.etree.ElementTree as ET
import zipfile

import html_converter

ns = {'ncx': 'http://www.daisy.org/z3986/2005/ncx/'}


class Page:
    def __init__(self, nav_point):
        self.nav_point = nav_point
        self.label = ''
        self.content = ''
        self.children = []
        self.load_page()

    def load_page(self):
        label_ncx = self.nav_point.find('ncx:navLabel', ns)
        if label_ncx:
            text_ncx = label_ncx.find('ncx:text', ns)
            if text_ncx is not None:
                self.label = text_ncx.text
        content_ncx = self.nav_point.find('ncx:content', ns)
        if content_ncx is not None:
            self.content = content_ncx.attrib['src']
        children = self.nav_point.findall('ncx:navPoint', ns)
        if children:
            for child in children:
                page = Page(child)
                self.children.append(page)


class EPub:
    def __init__(self, filename):
        self.filename = os.path.abspath(filename)
        self.contents = []

        self.epub_dir = tempfile.mkdtemp()
        if os.path.isfile(filename):
            zip = zipfile.ZipFile(filename)
            zip.extractall(self.epub_dir)
        else:
            # copytree requires the directory to not exist,
            # but mkdtemp creates an empty dir, so we just
            # delete and recreate it.
            shutil.rmtree(self.epub_dir)
            shutil.copytree(self.filename, self.epub_dir)

        self.toc_filename = os.path.join(self.epub_dir, "generated_epub_toc.html")
        self.read_toc()
        self.create_toc_page()

    def __del__(self):
        """
        Clean up the temp files when this object is destroyed.
        """
        shutil.rmtree(self.epub_dir)

    def create_toc_page(self):
        toc_html = html_converter.create_html_toc(self.contents)
        html = html_converter.create_html_page(toc_html)
        assert not os.path.exists(self.toc_filename)

        f = open(self.toc_filename, 'w')
        f.write(html)
        f.close()

        return self.toc_filename

    def read_toc(self):
        # FIXME: We should read META-INF/container.xml and the content.opf
        # file to determine the actual filename and path for the TOC
        toc_file = os.path.join(self.epub_dir, 'OEBPS', 'toc.ncx')
        if not os.path.exists(toc_file):
            toc_file = os.path.join(self.epub_dir, 'toc.ncx')
        root = ET.parse(toc_file)
        nav_map = root.find('ncx:navMap', ns)
        if nav_map:
            nav_points = nav_map.findall('ncx:navPoint', ns)
            for np in nav_points:
                page = Page(np)
                self.contents.append(page)

if __name__ == "__main__":
    epub = EPub(sys.argv[1])
    toc = html_converter.create_html_toc(epub.get_toc())
    print(html_converter.create_html_page(toc))

