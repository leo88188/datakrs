<?php

namespace app\admin\controller\ldcms;

use addons\ldcms\utils\builder\Form;
use app\admin\model\ldcms\Category as CategoryModel;
use app\admin\model\ldcms\Document as DocumentModel;
use app\admin\model\ldcms\Models as ModelsModel;
use fast\Tree;
use think\Db;
use think\Exception;

/**
 * 栏目管理
 *
 * @icon fa fa-circle-o
 */
class Category extends Base
{
    /**
     * Category模型对象
     * @var CategoryModel
     */
    protected $model = null;
    protected $categorys=null;
    protected $models=null;
    protected $model_names=[];
    protected $modelValidate=true;
    protected $multiFields="status,is_nav,sort";
    protected $noNeedRight=['getModels','getTitlePinyin','getUserLevels','getCategoryInfo'];

    protected $fields = null;


    public function _initialize()
    {
        parent::_initialize();
        $this->model = new CategoryModel();
        $modelsModel=new ModelsModel();
        $this->tree = Tree::instance();
        $this->tree->init(collection($this->model->where('lang',$this->lang)->order($this->model->getSort())->select())->toArray());
        $this->categorys = $this->tree->getTreeList($this->tree->getTreeArray(0), 'name');
        $this->view->assign("categorys", $this->categorys);
        $this->models=$modelsModel->getAdminList();
        $modelIds=[];
        foreach ($this->models as $key=>$model){
            $this->model_names[$model['id']]=$model['name'];
            $modelIds[]=$model['id'];
        }
        $this->assignconfig('modelsIds',$modelIds);
        $this->assignconfig('customColor', $modelsModel::getCustomColor());

        $this->fields = (new \app\admin\model\ldcms\CategoryFields())->getFieldsList();
    }



    /**
     * 默认生成的控制器所继承的父类中有index/add/edit/del/multi五个基础方法、destroy/restore/recyclebin三个回收站方法
     * 因此在当前控制器中可不用编写增删改查的代码,除非需要自己控制这部分逻辑
     * 需要将application/admin/library/traits/Backend.php中对应的方法复制到当前控制器,然后进行修改
     */


    /**
     * 查看
     */
    public function index()
    {
        //当前是否为关联查询
        $this->relationSearch = false;
        //设置过滤方法
        $this->request->filter(['strip_tags', 'trim']);
        if ($this->request->isAjax()) {
            foreach ($this->categorys as &$item){
                $item['mid_text']= isset($this->model_names[$item['mid']])?$this->model_names[$item['mid']]:'';
            }
            unset($item);
            $result = array("total" => count($this->categorys), "rows" => $this->categorys);

            return json($result);
        }
        return $this->view->fetch();
    }

    public function add()
    {
        if($this->request->isPost()){
            $params = $this->request->param('row/a');
            $this->addData($params);
            $this->success();
        }
        $pid=$this->request->param('pid');

        $categoryvalue=0;
        if(!empty($pid)){
            $categoryvalue=$pid;
        }
        $categorys=[
            0=>'顶级'
        ];
        foreach ($this->categorys as $cate){
            $categorys[$cate['id']]=$cate['name'];
        }
        $modelsModel=new ModelsModel();
        return Form::instance()
            ->fieldShow()
            ->setGroup('基础')
            ->setFormItem('type',__('Type'),'radio','',['content_list'=>[ 0=>'模型',1=>'链接']])
            ->setFormItem('pid',__('Pid'),'select','',['content_list'=>$categorys,'value'=>$categoryvalue])
            ->setFormItem('name',__('Name'),'string','required')
            ->setFormItem('ename',__('Ename'),'string')
            ->setFormItem('mid',__('Mid'),'select','required',['content_list'=>$this->model_names,'visible'=>'type=0'])
            ->setFormItem('urlname',__('Urlname'),'string','required',['visible'=>'type=0'])
            ->setFormItem('template_list',__('Template_list'),'selectpage','',function($data)use($modelsModel){
                $data['content_list']=json_encode($modelsModel->getTpl('list'));
                $data['visible']='type==0';
                return $data;
            })
            ->setFormItem('template_detail',__('Template_detail'),'selectpage','',function($data)use($modelsModel){
                $data['content_list']=json_encode($modelsModel->getTpl('detail'));
                $data['visible']='type=0';
                return $data;
            })
            ->setFormItem('outlink',__('Outlink'),'string','required',['visible'=>'type=1'])
            ->setFormItem('is_target',__('Is_target'),'switch','',['value'=>0,'visible'=>'type=1'])
            ->setFormItem('gid',__('Gid'),'selectpages','',[
                'content_list'=>url('ldcms/category/getUserLevels'),
                'setting'=>['primarykey'=>'id','field'=>'title'],
                'placeholder'=>'默认为公开'])
            ->setFormItem('status',__('Status'),'switch','',['value'=>1])
            ->setFormItems($this->fields)
            ->setGroup('高级')
            ->setFormItem('image',__('Image'),'images')
            ->setFormItem('big_image',__('栏目大图'),'images')
            ->setFormItem('seo_title',__('Seo_title'),'string')
            ->setFormItem('seo_keywords',__('Seo_keywords'),'string')
            ->setFormItem('seo_description',__('Seo_description'),'text')
            ->setFormItem('is_nav',__('Is_nav'),'switch','',['value'=>1])
            ->fetch();
    }

    public function adds()
    {
        if($this->request->isPost()){
            $params = $this->request->param('row/a');
            if(empty($params['name'])){
                $this->error('名称不能为空');
            }
            $namearr = json_decode($params['name'],true);
            if(empty($namearr)){
                $this->error('名称不能为空');
            }

            unset($params['name']);
            foreach ($namearr as $key=>$value){
                $params['name'] = $key;
                $params['urlname'] = $value;
                $this->addData($params);
            }

            $this->success();
        }
        $pid=$this->request->param('pid');

        $categoryvalue=0;
        if(!empty($pid)){
            $categoryvalue=$pid;
        }
        $categorys=[
            0=>'顶级'
        ];
        foreach ($this->categorys as $cate){
            $categorys[$cate['id']]=$cate['name'];
        }
        $modelsModel=new ModelsModel();
        return Form::instance()
            ->fieldShow()
            ->setFormItem('pid',__('Pid'),'select','',['content_list'=>$categorys,'value'=>$categoryvalue])
            ->setFormItem('name',__('Name'),'array','required',[
                'setting'=>['key'=>__('Name'),'value'=>__('Urlname')],
                'extend_html'=>'id="c-name"',
                'value'=>''
            ])
            ->setFormItem('mid',__('Mid'),'select','required',['content_list'=>$this->model_names])
            ->setFormItem('template_list',__('Template_list'),'selectpage','',function($data)use($modelsModel){
                $data['content_list']=json_encode($modelsModel->getTpl('list'));
                return $data;
            })
            ->setFormItem('template_detail',__('Template_detail'),'selectpage','',function($data)use($modelsModel){
                $data['content_list']=json_encode($modelsModel->getTpl('detail'));
                return $data;
            })
            ->fetch();
    }

    protected function addData($params){
        Db::startTrans();
        try {
            if (empty($params)) {
                throw new Exception(__('Parameter %s can not be empty', ''));
            }
            $params = $this->preExcludeFields($params);
            if ($this->dataLimit && $this->dataLimitFieldAutoFill) {
                $params[$this->dataLimitField] = $this->auth->id;
            }
            $params['lang']=$this->lang;

            //是否采用模型验证
            if ($this->modelValidate) {
                $name = str_replace("\\controller\\", "\\validate\\", get_class($this));
                $validate = is_bool($this->modelValidate) ? ($this->modelSceneValidate ? $name . '.add' : $name) : $this->modelValidate;
                $this->model->validateFailException()->validate($validate);
            }
            $result = $this->model->allowField(true)->create($params);
            if ($result === false) {
                throw new Exception($this->model->getError());
            }

            $id=$this->model->getLastInsID();
            //更新排序
            $up_result = $this->model->where('id','=',$id)->update(['sort'=>$id]);
            if ($up_result === false) {
                throw new Exception($this->model->getError());
            }

            /*如果选择了单页模型 则同时新增单页数据*/
            if($params['mid']==1){
                $pageData=[
                    'title'=>$params['name'],
                    'content'=>'',
                    'cid'=>$id,
                    'mid'=>$params['mid'],
                    'show_time'=>date('Y-m-d H:i:s'),
                    'lang'=>$params['lang']
                ];
                (new DocumentModel())->savePageData($pageData);
            }

            Db::commit();
            return true;
        }catch (\Exception $e){
            Db::rollback();
            $this->error($e->getMessage());
        }
    }

    public function del($ids=null)
    {
        $force = (int)$this->request->post("force");
        $ids=$this->request->post("ids/a");

        /*单个删除*/
        if (count($ids)==1){
            $row=$this->model->get($ids);
            /*如果是单页模型 直接删除*/
            if($row['mid']==1){
                parent::del($ids);
            }
        }

        $count=DocumentModel::instance()->where('cid', 'in', $ids)->count();
        if($count>0&&$force==0){
            $this->result([],2,'栏目下含有内容,不能删除');
        }
        parent::del($ids);
    }

    public function edit($ids = null)
    {
        if($this->request->isPost()){
            $postData=$this->request->post('row/a');
            $res=CategoryModel::validPid($postData['id'],$postData['pid']);
            if(!$res){
                $this->error('上级栏目不能选自身与子栏目');
            }
            parent::editPost($ids);
        }

        $categorys=[
            0=>'顶级'
        ];
        foreach ($this->categorys as $cate){
            $categorys[$cate['id']]=$cate['name'];
        }

        $modelsModel=new ModelsModel();
        $row=$this->model->get($ids);
        return Form::instance()
            ->fieldShow()
            ->setGroup('基础')
            ->setFormItem('id','','string','',['class'=>'hidden'])
            ->setFormItem('type',__('Type'),'radio','',['content_list'=>[ 0=>'模型',1=>'链接']])
            ->setFormItem('pid',__('Pid'),'select','',['content_list'=>$categorys])
            ->setFormItem('name',__('Name'),'string','required')
            ->setFormItem('ename',__('Ename'),'string')
            ->setFormItem('mid',__('Mid'),'select','required',['content_list'=>$this->model_names,'visible'=>'type=0'])
            ->setFormItem('urlname',__('Urlname'),'string','required',['visible'=>'type=0'])
            ->setFormItem('template_list',__('Template_list'),'selectpage','',function($data)use($modelsModel){
                $data['content_list']=json_encode($modelsModel->getTpl('list'));
                $data['visible']='type==0';
                return $data;
            })
            ->setFormItem('template_detail',__('Template_detail'),'selectpage','',function($data)use($modelsModel){
                $data['content_list']=json_encode($modelsModel->getTpl('detail'));
                $data['visible']='type=0';
                return $data;
            })
            ->setFormItem('outlink',__('Outlink'),'string','required',['visible'=>'type=1'])
            ->setFormItem('is_target',__('Is_target'),'switch','',['value'=>0,'visible'=>'type=1'])
            ->setFormItem('gid',__('Gid'),'selectpages','',[
                'content_list'=>url('ldcms/category/getUserLevels'),
                'setting'=>['primarykey'=>'id','field'=>'title'],
                'placeholder'=>'默认为公开'])
            ->setFormItem('status',__('Status'),'switch','',['value'=>1])
            ->setFormItems($this->fields)
            ->setGroup('高级')
            ->setFormItem('image',__('Image'),'images')
            ->setFormItem('big_image',__('栏目大图'),'images')
            ->setFormItem('seo_title',__('Seo_title'),'string')
            ->setFormItem('seo_keywords',__('Seo_keywords'),'string')
            ->setFormItem('seo_description',__('Seo_description'),'text')
            ->setFormItem('is_nav',__('Is_nav'),'switch','',['value'=>1])
            ->values($row)
            ->fetch();

    }

    public function getModels()
    {
        return $this->models;
    }

    /**
     * 获取标题拼音
     */
    public function getTitlePinyin()
    {
        $title = $this->request->post("title");
        //分隔符
        $delimiter = $this->request->post("delimiter", "");
        $pinyin = new \Overtrue\Pinyin\Pinyin('Overtrue\Pinyin\MemoryFileDictLoader');
        if ($title) {
            $result = $pinyin->permalink($title, $delimiter);
            $this->success("", null, ['pinyin' => $result]);
        } else {
            $this->error(__('Parameter %s can not be empty', 'name'));
        }
    }

    /**
     * 获取栏目信息
     * @param $id
     * @throws \think\db\exception\DataNotFoundException
     * @throws \think\db\exception\ModelNotFoundException
     * @throws \think\exception\DbException
     */
    public function getCategoryInfo($id)
    {
        $info=CategoryModel::find($id);
        $this->success("", null, $info);
    }

}
