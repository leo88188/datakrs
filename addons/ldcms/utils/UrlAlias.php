<?php

namespace addons\ldcms\utils;

class UrlAlias
{
    private static $publicToCms = [
        'services' => 'chanpinzhongxin',
        'products' => 'chanpinzhongxin',
        'solutions' => 'chanpinzhongxin',
        'pricing' => 'zaixianliuyan',
        'enterprise' => 'fuwutuandui',
        'resources' => 'xinwenzhongxin',
        'support' => 'lianxiwomen',
        'about' => 'guanyuwomen',
        'training' => 'fuwutuandui',
        'ecosystem' => 'fuwutuandui',
    ];

    public static function toCms($slug)
    {
        return self::$publicToCms[$slug] ?? $slug;
    }

    public static function toPublic($slug)
    {
        $cmsToPublic = [
            'chanpinzhongxin' => 'services',
            'anlizhanshi' => 'services',
            'zaixianliuyan' => 'pricing',
            'fuwutuandui' => 'enterprise',
            'xinwenzhongxin' => 'resources',
            'lianxiwomen' => 'support',
            'guanyuwomen' => 'about',
        ];
        $cmsToPublic['fuwutuandui'] = 'enterprise';
        return $cmsToPublic[$slug] ?? $slug;
    }
}
