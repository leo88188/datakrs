<?php

namespace addons\ldcms;

use addons\ldcms\model\Langs;
use addons\ldcms\utils\Common;
use addons\ldcms\utils\LdRoute;
use addons\ldcms\utils\Menu as LdcmsMenu;
use app\common\library\Menu;
use think\Addons;
use think\Config;
use think\Db;
use think\Route;

/**
 * 插件
 */
class Ldcms extends Addons
{
    use LdRoute;
    protected $menu = [
        [
            'name' => 'ldcms',
            'title' => '企业官网管理',
            'icon' => 'fa fa-desktop',
            'ismenu' => 1,
            'weigh' => 1,
            'sublist' => [
                [
                    'name' => 'ldcms/config',
                    'title' => '系统配置',
                    'remark' => '管理网站的系统配置信息,非开发人员请谨慎使用',
                    'icon' => 'fa fa-sliders',
                    'weigh' => 99,
                    'ismenu' => 1,
                    'sublist' => [
                        ['name' => 'ldcms/config/index', 'title' => '查看'],
                        ['name' => 'ldcms/config/add', 'title' => '添加'],
                        ['name' => 'ldcms/config/delcfg', 'title' => '删除'],
                    ],
                ],
                [
                    'name' => 'ldcms/site_info',
                    'title' => '站点信息',
                    'remark' => '用于管理网站的前台信息',
                    'icon' => 'fa fa-gear',
                    'weigh' => 95,
                    'ismenu' => 1,
                    'sublist' => [
                        ['name' => 'ldcms/site_info/index', 'title' => '查看'],
                        ['name' => 'ldcms/site_info/add', 'title' => '添加'],
                        ['name' => 'ldcms/site_info/delcfg', 'title' => '删除'],
                    ],
                ],
                [
                    'name' => 'ldcms/models',
                    'title' => '模型管理',
                    'remark' => '管理网站的模型与字段',
                    'icon' => 'fa fa-th-large',
                    'weigh' => 90,
                    'ismenu' => 1,
                    'sublist' => [
                        ['name' => 'ldcms/models/index', 'title' => '查看'],
                        ['name' => 'ldcms/models/add', 'title' => '添加'],
                        ['name' => 'ldcms/models/edit', 'title' => '编辑'],
                        ['name' => 'ldcms/models/del', 'title' => '删除'],
                        ['name' => 'ldcms/models/multi', 'title' => '批量更新']
                    ],
                ],
                [
                    'name' => 'ldcms/fields',
                    'title' => '字段管理',
                    'remark' => '用于管理模型的字段',
                    'icon' => 'fa fa-fields',
                    'ismenu' => 0,
                    'sublist' => [
                        ['name' => 'ldcms/fields/index', 'title' => '查看'],
                        ['name' => 'ldcms/fields/add', 'title' => '添加'],
                        ['name' => 'ldcms/fields/edit', 'title' => '修改'],
                        ['name' => 'ldcms/fields/del', 'title' => '删除'],
                        ['name' => 'ldcms/fields/multi', 'title' => '批量更新'],
                    ],
                ],
                [
                    'name' => 'ldcms/category',
                    'title' => '栏目管理',
                    'remark' => '管理网站的栏目与导航',
                    'icon' => 'fa fa-file-text-o',
                    'weigh' => 85,
                    'ismenu' => 1,
                    'sublist' => [
                        ['name' => 'ldcms/category/index', 'title' => '查看'],
                        ['name' => 'ldcms/category/add', 'title' => '添加'],
                        ['name' => 'ldcms/category/edit', 'title' => '编辑'],
                        ['name' => 'ldcms/category/del', 'title' => '删除'],
                        ['name' => 'ldcms/category/multi', 'title' => '批量更新'],
                        ['name' => 'ldcms/category/adds', 'title' => '批量添加'],

                    ],
                ],
                [
                    'name' => 'ldcms/document',
                    'title' => '内容管理',
                    'icon' => 'fa fa-list',
                    'weigh' => 80,
                    'ismenu' => 1,
                    'sublist' => [
                        ['name' => 'ldcms/document/index', 'title' => '查看'],
                        ['name' => 'ldcms/document/add', 'title' => '添加'],
                        ['name' => 'ldcms/document/edit', 'title' => '编辑'],
                        ['name' => 'ldcms/document/del', 'title' => '删除'],
                        ['name' => 'ldcms/document/multi', 'title' => '批量更新'],
                        ['name' => 'ldcms/document/move', 'title' => '移动'],
                        ['name' => 'ldcms/document/copy', 'title' => '复制'],
                        ['name' => 'ldcms/document/recyclebin', 'title' => '回收站'],
                        ['name' => 'ldcms/document/destroy', 'title' => '清空回收站'],
                        ['name' => 'ldcms/document/restore', 'title' => '还原'],
                        ['name' => 'ldcms/document/baidupush', 'title' => '百度推送'],
                        ['name' => 'ldcms/document/sensitive', 'title' => '敏感词查询'],
                        ['name' => 'ldcms/document/index/mid/1', 'title' => '单页内容', 'ismenu' => 1],
                        ['name' => 'ldcms/document/index/mid/2', 'title' => '新闻内容', 'ismenu' => 1],
                        ['name' => 'ldcms/document/index/mid/6', 'title' => '产品内容', 'ismenu' => 1],
                        ['name' => 'ldcms/document/index/mid/7', 'title' => '案例内容', 'ismenu' => 1],
                        ['name' => 'ldcms/document/index/mid/8', 'title' => '团队内容', 'ismenu' => 1],
                    ],
                ],
                [
                    'name' => 'ldcms/slider',
                    'title' => '轮播图管理',
                    'remark' => '用于管理站点的Banner图、幻灯片等',
                    'icon' => 'fa fa-photo',
                    'weigh' => 75,
                    'ismenu' => 1,
                    'sublist' => [
                        ['name' => 'ldcms/slider/index', 'title' => '查看'],
                        ['name' => 'ldcms/slider/add', 'title' => '添加'],
                        ['name' => 'ldcms/slider/edit', 'title' => '编辑'],
                        ['name' => 'ldcms/slider/del', 'title' => '删除'],
                        ['name' => 'ldcms/slider/multi', 'title' => '批量更新'],
                    ],
                ],
                [
                    'name' => 'ldcms/links',
                    'title' => '友情链接管理',
                    'icon' => 'fa fa-share-alt',
                    'remark' => '用于管理站点的友情链接，支持添加图片',
                    'weigh' => 70,
                    'ismenu' => 1,
                    'sublist' => [
                        ['name' => 'ldcms/links/index', 'title' => '查看'],
                        ['name' => 'ldcms/links/add', 'title' => '添加'],
                        ['name' => 'ldcms/links/edit', 'title' => '编辑'],
                        ['name' => 'ldcms/links/del', 'title' => '删除'],
                        ['name' => 'ldcms/links/multi', 'title' => '批量更新'],
                    ],
                ],
                [
                    'name' => 'ldcms/diyform',
                    'title' => '自定义表单管理',
                    'remark' => '支持创建表单，创建表单字段，但不会生成前台的表单HTML,需要手动制作form表单',
                    'icon' => 'fa fa-list',
                    'weigh' => 70,
                    'ismenu' => 1,
                    'sublist' => [
                        ['name' => 'ldcms/diyform/index', 'title' => '自定义表单列表', 'ismenu' => 1],
                        ['name' => 'ldcms/diyform/add', 'title' => '添加'],
                        ['name' => 'ldcms/diyform/edit', 'title' => '编辑'],
                        ['name' => 'ldcms/diyform/del', 'title' => '删除'],
                        ['name' => 'ldcms/diyform/multi', 'title' => '批量更新'],
                        [
                            'name' => 'ldcms/diyform_fields',
                            'title' => '自定义字段管理',
                            'icon' => 'fa fa-th-list',
                            'ismenu' => 0,
                            'sublist' => [
                                ['name' => 'ldcms/diyform_fields/index', 'title' => '查看'],
                                ['name' => 'ldcms/diyform_fields/add', 'title' => '添加'],
                                ['name' => 'ldcms/diyform_fields/edit', 'title' => '编辑'],
                                ['name' => 'ldcms/diyform_fields/del', 'title' => '删除'],
                                ['name' => 'ldcms/diyform_fields/multi', 'title' => '批量更新'],
                            ]
                        ],
                        [
                            'name' => 'ldcms/diyform_data',
                            'title' => '自定义表单数据',
                            'icon' => 'fa fa-list-alt',
                            'ismenu' => 0,
                            'sublist' => [
                                ['name' => 'ldcms/diyform_data/index', 'title' => '查看'],
                                ['name' => 'ldcms/diyform_data/add', 'title' => '添加'],
                                ['name' => 'ldcms/diyform_data/edit', 'title' => '编辑'],
                                ['name' => 'ldcms/diyform_data/del', 'title' => '删除'],
                                ['name' => 'ldcms/diyform_data/multi', 'title' => '批量更新'],
                            ]
                        ],
                    ],
                ],
                [
                    'name' => 'ldcms/content_url',
                    'title' => '内链管理',
                    'remark' => '自动替换生成文章正文内容中文本的链接',
                    'icon' => 'fa fa-random',
                    'weigh' => 65,
                    'ismenu' => 1,
                    'sublist' => [
                        ['name' => 'ldcms/content_url/index', 'title' => '查看'],
                        ['name' => 'ldcms/content_url/add', 'title' => '添加'],
                        ['name' => 'ldcms/content_url/edit', 'title' => '编辑'],
                        ['name' => 'ldcms/content_url/del', 'title' => '删除'],
                        ['name' => 'ldcms/content_url/multi', 'title' => '批量更新'],
                    ],
                ],
                [
                    'name' => 'ldcms/tags',
                    'title' => '内容Tags',
                    'remark' => '用于管理文章内容的tags标签',
                    'icon' => 'fa fa-tags',
                    'weigh' => 60,
                    'ismenu' => 1,
                    'sublist' => [
                        ['name' => 'ldcms/tags/index', 'title' => '查看'],
                        ['name' => 'ldcms/tags/add', 'title' => '添加'],
                        ['name' => 'ldcms/tags/edit', 'title' => '编辑'],
                        ['name' => 'ldcms/tags/del', 'title' => '删除'],
                        ['name' => 'ldcms/tags/multi', 'title' => '批量更新'],
                    ],
                ],
                [
                    'name' => 'ldcms/langs',
                    'title' => '多语言管理',
                    'remark' => '管理网站的多语言，默认自带中英文2种语言，如果新增语言会默认复制中文的"站点信息,前端语言文件"',
                    'icon' => 'fa fa-language',
                    'weigh' => 60,
                    'ismenu' => 1,
                    'sublist' => [
                        ['name' => 'ldcms/langs/index', 'title' => '查看'],
                        ['name' => 'ldcms/langs/add', 'title' => '添加'],
                        ['name' => 'ldcms/langs/edit', 'title' => '编辑'],
                        ['name' => 'ldcms/langs/del', 'title' => '删除'],
                        ['name' => 'ldcms/langs/multi', 'title' => '批量更新'],
                        ['name' => 'ldcms/langs/editLangFile', 'title' => '编辑语言文件'],
                    ],
                ],
                [
                    'name' => 'ldcms/category_fields',
                    'title'=>'自定义栏目字段',
                    'remark' => '',
                    'icon' => '',
                    'weigh' => 60,
                    'ismenu' => 0,
                    'sublist' => [
                        ['name' => 'ldcms/category_fields/index', 'title' => '查看'],
                        ['name' => 'ldcms/category_fields/add', 'title' => '添加'],
                        ['name' => 'ldcms/category_fields/edit', 'title' => '编辑'],
                        ['name' => 'ldcms/category_fields/del', 'title' => '删除'],
                        ['name' => 'ldcms/category_fields/multi', 'title' => '批量更新'],
                    ]
                ],
                [
                    'name' => 'ldcms/copy_langs',
                    'title' => '跨语言复制数据',
                    'remark' => '',
                    'icon' => '',
                    'weigh' => 60,
                    'ismenu' => 0,
                    'sublist' => [
                        ['name' => 'ldcms/copy_langs/index', 'title' => '查看'],
                        ['name' => 'ldcms/copy_langs/add', 'title' => '添加'],
                        ['name' => 'ldcms/copy_langs/edit', 'title' => '编辑'],
                        ['name' => 'ldcms/copy_langs/del', 'title' => '删除'],
                        ['name' => 'ldcms/copy_langs/multi', 'title' => '批量更新'],
                        ['name' => 'ldcms/copy_langs/category', 'title' => '复制栏目'],
                        ['name' => 'ldcms/copy_langs/document', 'title' => '复制内容'],
                    ],
                ],
                [
                    'name' => 'ldcms/themes',
                    'title' => '模板管理',
                    'remark' => '可上传安装（压缩包）、切换前台模板、下载模板备份、导入模板自带数据',
                    'icon' => 'fa fa-delicious',
                    'weigh' => 10,
                    'ismenu' => 1,
                    'sublist' => [
                        ['name' => 'ldcms/themes/index', 'title' => '查看'],
                        ['name' => 'ldcms/themes/local', 'title' => '上传安装'],
                        ['name' => 'ldcms/themes/install', 'title' => '直接安装'],
                        ['name' => 'ldcms/themes/enable', 'title' => '启用'],
                        ['name' => 'ldcms/themes/download', 'title' => '下载'],
                    ],
                ],
            ]
        ]
    ];

    /**
     * 插件安装方法
     * @return bool
     */
    public function install()
    {
        Menu::create($this->menu);
        $dir=ADDON_PATH . 'ldcms'.DS;
        /*site_info*/
        $file=$dir.'data'.DS.'site_info.zip';
        Common::unzip($dir.'data'.DS,$file);
        /*template*/
        $file=$dir.'view'.DS.'template_default.zip';
        Common::unzip($dir.'view'.DS,$file);
        $file=$dir.'view'.DS.'template_en.zip';
        Common::unzip($dir.'view'.DS,$file);

        /*设置网站主域名*/
        $config=get_addon_config('ldcms');
        if(empty($config['main_domain'])){
            $config['main_domain']=request()->host();
            set_addon_config('ldcms',$config);
        }
        return true;
    }

    /**
     * 插件卸载方法
     * @return bool
     */
    public function uninstall()
    {
        Menu::delete("ldcms");
        return true;
    }

    /**
     * 插件启用方法
     * @return bool
     */
    public function enable()
    {
        Menu::enable("ldcms");
        return true;
    }

    /**
     * 插件禁用方法
     * @return bool
     */
    public function disable()
    {
        Menu::disable("ldcms");
        return true;
    }

    /**
     * 插件升级方法
     * @return bool
     */
    public function upgrade()
    {
        //如果菜单有变更则升级菜单
//        Menu::upgrade('ldcms', $this->menu);
        $dir=ADDON_PATH . 'ldcms'.DS.'data'.DS;
        $file =  $dir. 'site_info.zip';
        @unlink($file);
        /*升级时删除模板压缩包*/
        $dir=ADDON_PATH . 'ldcms'.DS.'view'.DS;
        @unlink($dir. 'template_default.zip');
        @unlink($dir. 'template_en.zip');

        /*更新菜单*/
        $this->updateMenu();
        /*升级时更新默认语言*/
        $langsModel=Db::name('ldcms_langs');
        if(!$langsModel->where('is_default',1)->count()){
            $langsModel->where('code','zh-cn')->update(['is_default'=>1]);
        }
        /*升级系统配置文件*/
        $this->updateConfig();
        return true;
    }

    /**
     * 应用初始化
     */
    public function appInit()
    {
        //后期废弃函数库
        include_once ADDON_PATH . 'ldcms' . DS . 'common.php';
        //替换上面的函数库，函数名增加了标识ld_
        include_once ADDON_PATH . 'ldcms' . DS . 'ldfunc.php';
        $config = get_addon_config('ldcms');
        $taglib = Config::get('template.taglib_pre_load');
        Config::set('template.taglib_pre_load', ($taglib ? $taglib . ',' : '') . 'addons\\ldcms\\taglib\\Ld');
        /*设置默认语言*/
        $config['default_lang']=Langs::instance()->getDefaultLang();
        $config['langs']=Langs::instance()->getList();
        $config['lang_list']=Langs::instance()->lists();
        Config::set('ldcms', $config);

        $this->routeLang($config);
    }

    public function configInit(&$param)
    {
        $param['ldcms'] = ['langs' => Config::get('ldcms.langs')];
    }

//    升级系统配置
    protected function updateConfig(){
        $full_config=get_addon_fullconfig('ldcms');
        $config=get_addon_config('ldcms');
        $config_key=array_keys($config);
        $update_config=include ADDON_PATH . 'ldcms' . DS . 'update_config.php';
        foreach ($update_config as $v){
            /*如果名称存在则不进行添加*/
            if(!in_array($v['name'],$config_key)){
                array_push($full_config,$v);
            }
        }
        /*自动设置主域名*/
        foreach ($full_config as &$v){
            if($v['name']=='main_domain'&&empty($v['value'])){
                $v['value']=request()->host();
            }
        }
        set_addon_fullconfig('ldcms',$full_config);
    }

    protected function updateMenu(){
        $upmenu=[
            [
                'name' => 'ldcms/slider',
                'title' => '轮播图管理',
                'remark' => '用于管理站点的Banner图、幻灯片等',
                'icon' => 'fa fa-photo',
                'weigh' => 75,
                'ismenu' => 1,
                'sublist' => [
                    ['name' => 'ldcms/slider/index', 'title' => '查看'],
                    ['name' => 'ldcms/slider/add', 'title' => '添加'],
                    ['name' => 'ldcms/slider/edit', 'title' => '编辑'],
                    ['name' => 'ldcms/slider/del', 'title' => '删除'],
                    ['name' => 'ldcms/slider/multi', 'title' => '批量更新'],
                ],
            ]
        ];
        LdcmsMenu::update('ldcms', 'ldcms/ad',$upmenu);

        $upmenu=[
            [
                'name' => 'ldcms/category',
                'title' => '栏目管理',
                'remark' => '管理网站的栏目与导航',
                'icon' => 'fa fa-file-text-o',
                'weigh' => 85,
                'ismenu' => 1,
                'sublist' => [
                    ['name' => 'ldcms/category/index', 'title' => '查看'],
                    ['name' => 'ldcms/category/add', 'title' => '添加'],
                    ['name' => 'ldcms/category/edit', 'title' => '编辑'],
                    ['name' => 'ldcms/category/del', 'title' => '删除'],
                    ['name' => 'ldcms/category/multi', 'title' => '批量更新'],
                    ['name' => 'ldcms/category/adds', 'title' => '批量添加'],

                ],
            ]
        ];
        LdcmsMenu::update('ldcms', 'ldcms/category',$upmenu);

        $ids = LdcmsMenu::getAuthRuleIdsByName('ldcms/copy_langs');
        if(empty($ids)){
            $createMenu=[
                [
                    'name' => 'ldcms/copy_langs',
                    'title' => '跨语言复制数据',
                    'remark' => '',
                    'icon' => '',
                    'weigh' => 60,
                    'ismenu' => 0,
                    'sublist' => [
                        ['name' => 'ldcms/copy_langs/index', 'title' => '查看'],
                        ['name' => 'ldcms/copy_langs/add', 'title' => '添加'],
                        ['name' => 'ldcms/copy_langs/edit', 'title' => '编辑'],
                        ['name' => 'ldcms/copy_langs/del', 'title' => '删除'],
                        ['name' => 'ldcms/copy_langs/multi', 'title' => '批量更新'],
                        ['name' => 'ldcms/copy_langs/category', 'title' => '复制栏目'],
                        ['name' => 'ldcms/copy_langs/document', 'title' => '复制内容'],
                    ]
                ]
            ];
            LdcmsMenu::create($createMenu,'ldcms');
        }

        $ids = LdcmsMenu::getAuthRuleIdsByName('ldcms/category_fields');
        if(empty($ids)){
            $createMenu=[
                [
                    'name' => 'ldcms/category_fields',
                    'title'=>'自定义栏目字段',
                    'remark' => '',
                    'icon' => '',
                    'weigh' => 60,
                    'ismenu' => 0,
                    'sublist' => [
                        ['name' => 'ldcms/category_fields/index', 'title' => '查看'],
                        ['name' => 'ldcms/category_fields/add', 'title' => '添加'],
                        ['name' => 'ldcms/category_fields/edit', 'title' => '编辑'],
                        ['name' => 'ldcms/category_fields/del', 'title' => '删除'],
                        ['name' => 'ldcms/category_fields/multi', 'title' => '批量更新'],
                    ]
                ]
            ];
            LdcmsMenu::create($createMenu,'ldcms');
        }

        $ids = LdcmsMenu::getAuthRuleIdsByName('ldcms/themes');
        if(empty($ids)){
            $createMenu=[
                [
                    'name' => 'ldcms/themes',
                    'title' => '模板管理',
                    'remark' => '可上传安装（压缩包）、切换前台模板、下载模板备份、导入模板自带数据',
                    'icon' => 'fa fa-delicious',
                    'weigh' => 10,
                    'ismenu' => 1,
                    'sublist' => [
                        ['name' => 'ldcms/themes/index', 'title' => '查看'],
                        ['name' => 'ldcms/themes/local', 'title' => '上传安装'],
                        ['name' => 'ldcms/themes/install', 'title' => '直接安装'],
                        ['name' => 'ldcms/themes/enable', 'title' => '启用'],
                        ['name' => 'ldcms/themes/download', 'title' => '下载'],
                    ],
                ],
            ];
            LdcmsMenu::create($createMenu,'ldcms');
        }
    }
}