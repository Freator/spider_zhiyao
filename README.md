# 爬虫学习--知妖网站数据爬取

Python爬虫在笔者学习Python时接触过并且也使用过（见 [豆瓣数据爬取作业](https://github.com/Freator/Homework_DoubanSpider)），但是并没有比较系统的学习，现在算是从最简单的网站爬取开始学习。**前路漫漫，当积跬步，先行百里，再至千里**。

## 一 爬取网站介绍

[知妖（中国妖怪百集）](http://www.cbaigui.com/)，是一个开放的在线“妖怪”资料库，致力于收集、整理、介绍、分享古人文献中的“妖怪”，算是个私人非营利性的网站。网站上的内容分享都是自由开放的，无需注册或付费，鉴于里面的图片数据，在[关于授权](http://www.cbaigui.com/?page_id=4635)中有说明，是需要授权才能下载使用的，所以本次爬取的数据只包括**文本数据**。网站的网页源码就是简单的HTML，在初学爬虫的时候，笔者以为爬取此类网站是比较容易入手的。

## 二 网站数据分析

首先，我们进入到知妖网站的主页，可以看到，主页上主要分为`首页`、`目录`、`杂谈`、`夜谭`、`关于`等5个板块，在主页（即首页）上，各种妖怪们按顺序排列，每页大概20来个，目前一共85页。

![网站主页](./pictures/zhiyao_MainPage.png)

当然可以按照这个页数来爬取每一个妖怪的数据，但是本次我们是分目录爬取的，即先进入`目录`页面。

![目录页面](./pictures/zhiyao_category_list.png)

可以看到各个按照字母索引的书名目录。每一个书名点进去就是这个书名下包含的妖怪们，如 `白泽图` ，点进去是这样的

![目录内容](./pictures/zhiyao_category_show.png)

在这个页面上，我们可以看到这个书名目录下包含的每一个妖怪的一些基本数据，本次所需要爬取的数据如标注所示

![妖怪列表](./pictures/zhiyao_article_list.png)

其中`[1][2][3]`部分是我们需要爬取的数据，分别表示该妖怪发表的日期，该妖怪的名字和该妖怪的评论数量。（其他数据也可以按照自己的需求进行爬取）

然后点进一个妖怪，进入到这个妖怪的介绍页面，如 `升卿` ，点进去之后，可以看到它的介绍，包括`发表日期`（所以日期数据在这里也可以获取），图片（部分有部分没有）、出处及原文描述，下面还有`获赞数量`，该妖怪所属的`Tags`，以及具体的评论文字（评论没有分页展示，需要爬取的话也比较方便）

![妖怪展示页面](./pictures/zhiyao_article_show1.png)

![妖怪展示页面](./pictures/zhiyao_article_show2.png)

![妖怪展示页面](./pictures/zhiyao_article_show3.png)

## 三 爬取简单流程

1. 直接进入到目录页面下，先获取目录中的所有书名目录（网页源码中包含每一个目录的ID，一并获取）
2. 进入到每一个目录下，获取所有该目录下所有的妖怪，包括该妖怪发表日期，妖怪名称，评论数量（网页源码中还包含妖怪ID，可以一并获取）
3. 进入到该目录下每一个妖怪的介绍页面，获取点赞数、Tags两个字段（其他数据可以根据自己的需要爬取）
4. 循环第`2` 和第`3`步，直到所有的书名目录和该目录下的妖怪全部被爬取
5. 得到的每一个妖怪数据应该包括：`妖怪ID`，`妖怪名称`，`书名目录ID`，`书名目录名称`，`发表日期`，`Tags`，`评论数量`，`点赞数量`。保存到文件中。  

## 四 网页源码分析

### 1 目录页面

打开开发者模式(`Chrome`和`Firefox`都可以直接按`F12`打开)，刷新当前页面，可以看到该网页是以`GET`方式请求得到的，并且是一个简单的`HTML`页面

![html_analysis1](./pictures/html_analysis1.png)

然后我们转到`Elements`中，看到我们需要爬取的内容，通过标签一级一级找下来，都在`class="entry themeform"`的`div`标签中，如下图所示

![html_analysis2](./pictures/html_analysis2.png)

然后，我们再打开比如`B`类下的`table`标签，可以看到里面的内容，就是包含这个内容索引下的所有书名目录，这些是我们需要爬取并保存的内容

![html_analysis3](./pictures/html_analysis3.png)

这里我们需要爬取每一个书名目录所属的字母索引，每个书名目录的名称和对应的`URL`备用，可以从图中看到每一个书名目录是包含在`strong`标签下的，所以就找到这个标签下的所有`a`标签，保存该标签的`href`属性和标签内容就行（当然也有其他方式方法可以找这些数据）

### 2 书名目录页面

还是以`白泽图`为例，同样可以看到是以`GET`请求获取的`HTML`内容。

![html_analysis4](./pictures/html_analysis4.png)

转到`Elements`下，可以找到需要获取的内容。从图中可以看出，每一个妖怪的数据都在一个`article`标签内。

![html_analysis5](./pictures/html_analysis5.png)

打开其中一个`article`标签，可以看到里面包括我们要获取的日期数据，妖怪姓名，评论数量，以及妖怪的`ID`等。

![html_analysis6](./pictures/html_analysis6.png)

### 3 妖怪介绍页面

同样以`升卿`为例，进入到该妖怪的介绍页面，依然是以`GET`方式请求的`HTML`网页。在`Element`中，找到所需要的标签内容，如下图所示。

![html_analysis7](./pictures/html_analysis7.png)

![html_analysis8](./pictures/html_analysis8.png)

## 五 爬取程序

程序中主要用到的是`requests`和`beautifulsoup`两个包，当然，还有许多其他的包可以用来做这个项目，有兴趣的可以自行学习和使用。笔者以为，不管是自己一步一步敲出来的爬虫还是运用的一些成熟的爬虫框架，其原理和机制都是差不多的，只要大家根据爬虫原理来做，逻辑上就不会有什么大问题。该爬虫的具体流程可以查看第`三`点说明。下面解释程序中的各个函数功能。

+ get_html(current_url)

  该函数用于获取`HTML`网页的文本内容

  参数：网页的`URL`

  返回：网页响应状态为`200`时，返回文本内容；否则，返回 None

+ find_all_table_data(table_label)

  该函数用于获取某一个大类索引下的所有目录列表，比如`B`类下的所有书名目录和对应的目录`URL`。

  参数：一个`table`标签的内容

  返回：一个`list`，列表元素是由（书名目录名称，书名目录链接）组成的一个`tuple`。

+ get_article_data(article)

  该函数用于获取每一个妖怪的数据

  参数：一个`article`标签内容

  返回：一个`tuple`，包括妖怪的各种信息数据(第`三`部分第`5`点)。

+ get_more_article_data(article_url)

  该函数从妖怪展示页面获取妖怪的获赞数和`Tags`数据

  参数：妖怪展示页面的`URL`

  返回：`tags_list`, `like_count`，即`Tags`列表和获赞数

+ jump_to_article_page(article_id)

  该函数通过妖怪`ID`得到该妖怪的展示页面`URL`并调用`get_more_article_data`函数获取数据

  参数：妖怪`ID`

  返回：同`get_more_article_data`函数

+ get_category(index_url)

  该函数获取每一个字母索引类别下的书名目录

  参数：目录页面的`URL`

  返回：`Dict`，其中`key`是每个字母，`value`是一个`list`，保存该字母下的所有书名目录

+ write_to_file(article_tuple)

  将每一个妖怪数据写入文件

  参数：`tuple`，包含一个妖怪的所有需要保存的数据

+ get_first_page_article(current_category_url)

  获取当前书名目录下的所有`article`标签

  参数：当前书名目录的`URL`

  返回：如果页面存在，则返回`list`，书名目录名称；否则，返回`None`,`None`

+ get_other_page_article(current_category, category_name)

  类似于`get_first_page_article`函数，但是这个函数是在该书名目录中的妖怪数量有多页展示时，爬取第`2-last`页面的函数，可以看到参数不一样，这个函数多了一个书名目录名称参数。

  返回：成功，返回`True`页面查找失败返回`False`

+ get_data(category_list)

  该函数获通过`main`函数调用，获取每个书名目录的数据

  参数：书名目录`list`

  返回：成功返回`True`；否则返回`False`

+ main(begin_url)

  主函数，通过传入目录页面`URL`，调用`get_data`函数开始爬取和保存数据

## 六 思考

1. python编写程序的规范问题，以及python作为面向对象的语言，如何更规范的编写函数，设定参数，设置返回值等
2. 效率问题。目前爬虫只是解决了最简单的问题，而且网站的数据量极小，如果遇上大量数据的爬取工作，如果设置更加有效率的爬虫，是否需要使用多线程或者多进程进行爬取数据。
3. 文件操作。其实还是效率问题，爬取的数据如何高效的保存，写入到文件（包括但不限于txt/csv/excel/json）或者数据库（包括但不限于MySQL/Oracle/MongoDB/Redis/SQL Server）
4. 容错机制。爬取的过程中，遇到某一个无法访问的页面，或者时该页面下不存在某个标签（实际在爬取过程中确实存在这样的情况），如何设置跳过或者捕获该错误，让程序继续运行，直至数据爬取完成。如果不设置，程序在运行的过程中遇到错误，则会终止运行。
5. 爬虫终究只是获取数据的一种方式/工具。在获取数据后，如何进行数据处理，利用数据分析现象，发掘有价值的信息，这是笔者以为比较重要和关键的，如果爬取的数据不加以挖掘和分析，数据也只会是数据而已。

@Date : 2020/5/17（Update : 2020/5/27）

@Author : [Freator Tang](https://github.com/Freator)

@Email : [bingcongtang@gmail.com](mailto:bingcongtang@gmail.com)
