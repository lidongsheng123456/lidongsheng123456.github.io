import { viteBundler } from '@vuepress/bundler-vite';
import { defineUserConfig } from "vuepress";
import recoTheme from "vuepress-theme-reco";

export default defineUserConfig({
  base: '/Blog/',
  title: "东sheng&",
  description: "Just playing around",
  bundler: viteBundler(),
  // bundler: webpackBundler(),
  theme: recoTheme({
    primaryColor: 'pink',
    locales: undefined, socialLinks: undefined,
    style: "@vuepress-reco/style-default",
    logo: "/logo.png",
    author: "li dong sheng",
    authorAvatar: "/logo.png",
    docsRepo: "https://github.com/lidongsheng123456",
    docsBranch: "main",
    docsDir: "./docs",
    lastUpdatedText: "",
    // series 为原 sidebar
    series: {
      '/vuepress-theme-reco/': ['introduce', 'usage']
    },
    navbar: [
      { text: '主页', link: '/' },
      { text: '时间线', link: '/timeline.html' },
      { text: '关于踩坑这件事', link: '/docs/踩坑/pit.html' },
      { text: '冷知识', link: '/docs/冷知识/trivia.html' },
      { text: 'gitee', link: 'https://gitee.com/li-dongshenger' },
    ],
    commentConfig: {
      type: 'valine',
      options: {
        appId: 'J57SL4NyJLrPuQa6grpZEOeA-gzGzoHsz', // your appId
        appKey: 'fZSjKlcrDF5diSivbvKfRCJc', // your appKey
        // hideComments: true, // 全局隐藏评论，默认 false
      },
    },
    // bulletin: {
    //     body: [
    //         {
    //             type: 'text',
    //             content: `
    //                     <div style="padding: 1rem; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;">
    //                       <h3 style="margin:0 0 1.5rem 0; padding-bottom:0.5rem; padding-top: 0;border-bottom:2px solid #f0f0f0; font-size:1.2em; color:#2c3e50;">📁 项目速览</h3>
    //                       <div style="margin:1.2rem 0; padding:1rem; background:#f8f8f8; border-radius:6px;">
    //                         <div style="font-size:0.9em; color:#666; margin-bottom:0.5rem;">
    //                           <span style="color:#6db33f;">SpringBoot3</span>+<span style="color:#42b883;">Vue3</span>
    //                           <a href='https://gitee.com/li-dongshenger/web_manage/stargazers'><img style="width: 80px;height: 20px" src='https://gitee.com/li-dongshenger/web_manage/badge/star.svg?theme=dark' alt='star'></a>
    //                         </div>
    //                         <h4 style=" color:#2c3e50; font-size:1.1em;margin: 0;padding: 10px 0">东神脚手架</h4>
    //                         <div style="font-size:0.9em;">
    //                           <time style="color:#666;">2025.01.15-02.03</time><br>
    //                           <a href="http://139.196.196.178:82" 
    //                              target="_blank" 
    //                              style="color:#42b983; text-decoration:none; transition:opacity 0.2s;"
    //                              rel="noopener noreferrer">
    //                             在线预览 ➔
    //                           </a>
    //                         </div>
    //                       </div>

    //                       <div style="margin:1.2rem 0; padding:1rem; background:#f8f8f8; border-radius:6px;">
    //                         <div style="font-size:0.9em; color:#666; margin-bottom:0.5rem;">
    //                           <span style="color:#6db33f;">SpringBoot2</span>+<span style="color:#42b883;">Vue2</span>
    //                         </div>
    //                         <h4 style="color:#2c3e50; font-size:1.1em;margin: 0;padding: 10px 0">非遗智创社区</h4>
    //                         <div style="font-size:0.9em;">
    //                           <time style="color:#666;">2025.02.05-02.20</time><br>
    //                           <a href="http://www.intangible-culture.top:81"
    //                              target="_blank"
    //                              style="color:#42b983; text-decoration:none; transition:opacity 0.2s;"
    //                              rel="noopener noreferrer">
    //                             访问项目 ➔
    //                           </a>
    //                         </div>
    //                       </div>

    //                       <div style="margin-top:1.5rem; display:grid; gap:0.8rem;">
    //                         <a href="https://gitee.com/li-dongshenger" 
    //                            target="_blank"
    //                            style="display:flex; align-items:center; gap:0.5rem; color:#666; text-decoration:none; padding:0.6rem; background:#f5f5f5; border-radius:4px;">
    //                           <span style="font-size:1.2em;">📦</span>代码仓库
    //                         </a>
    //                         <a href="http://www.jitingfeng.top"
    //                            target="_blank"
    //                            style="display:flex; align-items:center; gap:0.5rem; color:#666; text-decoration:none; padding:0.6rem; background:#f5f5f5; border-radius:4px;">
    //                           <span style="font-size:1.2em;">🤝</span>友情链接
    //                         </a>
    //                       </div>
    //                     </div>
    //                           `,
    //             style: 'font-size: 14px;'
    //         }
    //     ]
    // }
  }),
  head: [
    ['link', { rel: "stylesheet", href: "/css/style.css" }],
    [
      'script',
      {},
      `
            var _hmt = _hmt || [];
            (function() {
                var hm = document.createElement("script");
                hm.src = "https://hm.baidu.com/hm.js?88bfdefb28c178833b189aa63cb487a6";
                var s = document.getElementsByTagName("script")[0]; 
                s.parentNode.insertBefore(hm, s);
            })();
            `
    ],
    ["link", { rel: "icon", href: 'logo.png' }]
  ],
  // debug: true,
});
