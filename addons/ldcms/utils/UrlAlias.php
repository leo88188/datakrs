<?php

namespace addons\ldcms\utils;

class UrlAlias
{
    private static $publicToCms = [
        'products' => 'chanpinzhongxin',
        'solutions' => 'anlizhanshi',
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
        $cmsToPublic = array_flip(self::$publicToCms);
        $cmsToPublic['fuwutuandui'] = 'enterprise';
        return $cmsToPublic[$slug] ?? $slug;
    }
}
