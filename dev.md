https://www.medchemexpress.com/ 网站结构目录进行爬取

入口和类型：

类型1
https://www.medchemexpress.com/pathway.html

类型2 
页面相似
https://www.medchemexpress.com/NaturalProducts/Natural%20Products.html
https://www.medchemexpress.com/oligonucleotides.html
https://www.medchemexpress.com/isotope-compound/isotope-compound.html
https://www.medchemexpress.com/dyereagents/dye-reagents.html
https://www.medchemexpress.com/inhibitory-antibodies.html
https://www.medchemexpress.com/biochemical-assay-reagents.html
https://www.medchemexpress.com/antibodies.html
https://www.medchemexpress.com/enzyme.html

类型2-2
https://www.medchemexpress.com/standards.html

类型3
https://www.medchemexpress.com/peptides.html
https://www.medchemexpress.com/induced-disease-model.html

类型4：
https://www.medchemexpress.com/gmp-small-molecules/gmp-molecules-for-cell-and-gene-therapy-cgt.html




开发和测试：
一个阶段一个阶段的来爬取

开发结构
页面爬取 + 内容爬取 组合的交互式爬取方案

线程：一个入口一个线程



数据表：
任务队列表（页面 + url）
页面 url，url_key, short_url(name?)
processing: waiting/running/complete/(failed)
task_key:thread_name 标准化后的结果 用于多线程任务的执行


专题目录
数字数量（可以忽略）
原标题
name
短url
完整url

目录分两类：1 分类  2 标签

group_name 和 thread_name 的区别
thread_name 指的是每一个入口url最后一级路由
group：thread_name 所属组的key






代理：复用aist的代理检测的结果


页面分类：
pathways_top: 
https://www.medchemexpress.cn/pathway.html
特点：
div class=pathway_list




一些隐藏的属性;pdf-name-width


通用：
当前标题：id = category_tit


pathways
i

