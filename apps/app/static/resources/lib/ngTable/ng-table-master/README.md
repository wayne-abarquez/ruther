Table + AngularJS
=================
[![Build Status](https://travis-ci.org/esvit/ng-table.png)](https://travis-ci.org/esvit/ng-table) [![Coverage Status](https://coveralls.io/repos/esvit/ng-table/badge.png)](https://coveralls.io/r/esvit/ng-table)

Code licensed under New BSD License.

This directive allow to liven your tables. It support sorting, filtering and pagination.
Header row with titles and filters automatic generated on compilation step.

<a href='http://www.pledgie.com/campaigns/22338'><img alt='Click here to lend your support to: ngTable and make a donation at www.pledgie.com !' src='http://www.pledgie.com/campaigns/22338.png?skin_name=chrome' border='0' /></a>

## Updates

### v0.3.0
- I abandoned from CoffeeScript in favor of a javascript, fully agree with http://blog.ponyfoo.com/2013/09/28/we-dont-want-your-coffee & (rus) http://habrahabr.ru/post/195944/
- added examples of table with grouping
- fully rewrited interface of ngTableParams

### v0.2.2
In functions that return data for the filters were removed `.promise`
```
$scope.names = function(column) {
    ...
    def.resolve(names);
    // return def.promise; - old code
    return def;
};
```


## Installing via Bower
```
bower install ng-table
```

## Examples (from simple to complex)

* [Pagination](http://esvit.github.io/ng-table/#!/demo1)
* [Sorting](http://esvit.github.io/ng-table/#!/demo3)
* [Filtering](http://esvit.github.io/ng-table/#!/demo4)
* [Cell template](http://esvit.github.io/ng-table/#!/demo8)
* [Row template](http://esvit.github.io/ng-table/#!/demo9)
* [Params in url](http://esvit.github.io/ng-table/#!/demo5)
* [Ajax](http://esvit.github.io/ng-table/#!/demo6)
* [Custom template(pagination)](http://esvit.github.io/ng-table/#!/demo2)
* [Custom filters](http://esvit.github.io/ng-table/#!/demo11)
* [Table with checkboxes](http://esvit.github.io/ng-table/#!/demo10)

## Usage
```html
<table ng-table="tableParams" show-filter="true">
<tr ng-repeat="user in users">
    <!-- IMPORTANT: String titles must be in single quotes -->
    <td data-title="'Name of person'" filter="{ 'name': 'text' }" sortable="name">
        {{user.name}}
    </td>
    <td data-title="'Age'" filter="{ 'action': 'button' }" sortable="age">
        {{user.age}}
    </td>
</tr>
</table>
```
