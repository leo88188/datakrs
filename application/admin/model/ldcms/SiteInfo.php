<?php


namespace app\admin\model\ldcms;


use addons\ldcms\model\common\Backend;

class SiteInfo extends Backend
{
    protected $name='ldcms_siteinfo';

    protected $type=['config'=>'array'];

    /**
     * 保存配置
     * @param $data
     * @param $lang
     * @throws \think\db\exception\DataNotFoundException
     * @throws \think\db\exception\ModelNotFoundException
     * @throws \think\exception\DbException
     */
    public function setConfig($data,$lang){
        $res=$this->where('lang',$lang)->find();
        if($res){
            $res->save(['config'=>$data]);
        }else{
            $this->save(['lang'=>$lang,'config'=>$data]);
        }
    }
    public function getConfig($lang)
    {
        $res=$this->where('lang',$lang)->find();
        return $res['config'];
    }
}