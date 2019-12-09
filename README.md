
### Usage:

```bash
python3 app.py --nc=XX --pc=YYY --township="Englewood"
```

To get neighborhood code and property class go to https://www.cookcountyassessor.com/Search/Property-Search.aspx
find your property.  When you pull up your property you will see:


```bash
Township: West Chicago
Property Classification: 211
...
Neighborhood: 30
```

### Release Notes

I really hate Selenium hacks and I make a point to not use them anymore, however-
this is some old code lying around that might help other people in Chicago, and I 
don't care enough to refactor Selenium out of it. So use it or don't, IDGAF.

I also will probably not do to much to maintain / update this until I need it again, but 
in the mean time- if you find it useful, give it a star. 

### Requirements

- Selenium Web Driver
- Firefox
