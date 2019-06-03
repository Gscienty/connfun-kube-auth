# connfun-kube-auth

* REDIS\_HOST redis Host


维护一个统一的 common account 集合，集合中每个元素的样式如下：
```
{
    id: <account id>,
    support: [ <supported type> ],
    role: [ <role collection> ],
    lock_expired: <lock expire timestamp>
}
```

各个具体的认证模式下，必须包括有 common account的ID，例如password模式
```
{
    account_name: <username>,
    hash_algo: <hash algorithm name>,
    password: <password>,
    refer_account_id: <id>
}
```
