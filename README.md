# vpn-switch
Switch vpn on/off as an workflow of alfred

![image][demo-gif]


## Usage
- vsetkey \<shared-secret-key\> -- set the shared secret key for L2TP vpn.
- vpn \[\<query\>\] -- list the available vpn in Network Preferences, as well as some convience action items.

## feature
- \<query\> is used to filter the matching vpn, select one item and press enter will connect the selected vpn.
- If no query is entered, and no vpn is connected, the first item is set to connect vpn in order until success.
- when vpn is connected, the first action item is set to stop it for convinience.
- only support PPTP and L2TP


## Thanks
It is based on the [Alfred-Workflow][alfred-workflow] library


[alfred-workflow]: https://github.com/deanishe/alfred-workflow
[demo-gif]: /packal/vpn-switch-record.gif
