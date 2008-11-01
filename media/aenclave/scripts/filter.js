function option(value,text) {
  var node = document.createElement("option");
  node.setAttribute("value",value);
  node.appendChild(document.createTextNode(text));
  return node;
}

function button(value,action) {
  var node = document.createElement("input");
  node.setAttribute("type","button");
  node.setAttribute("value",value);
  node.setAttribute("onclick",action);
  return node;
}

function kind_select() {
  var node = document.createElement("select");
  node.id = "str";
  node.setAttribute("onchange","change_kind(this);");
  node.appendChild(option("title","Song title"));
  node.appendChild(option("album","Album name"));
  node.appendChild(option("artist","Artist name"));
  node.appendChild(option("track","Track number"));
  node.appendChild(option("time","Song duration"));
  node.appendChild(option("date_added","Date added"));
  node.appendChild(option("last_queued","Last queued"));
  node.appendChild(option("and","Satisfies all"));
  node.appendChild(option("nand","Doesn't satisfy all"));
  node.appendChild(option("or","Satisfies any"));
  node.appendChild(option("nor","Doesn't satisfy any"));
  return node;
}

function rule_select(cat) {
  var node = document.createElement("select");
  node.setAttribute("onchange","change_rule(this);");
  if (cat == "str") {
    node.id = "str";
    node.appendChild(option("in","contains"));
    node.appendChild(option("notin","doesn't contain"));
    node.appendChild(option("start","starts with"));
    node.appendChild(option("notstart","doesn't start with"));
    node.appendChild(option("end","ends with"));
    node.appendChild(option("notend","doesn't end with"));
    node.appendChild(option("is","is"));
    node.appendChild(option("notis","is not"));
  } else if (cat == "int") {
    node.id = "range";
    node.appendChild(option("inside","is within range"));
    node.appendChild(option("outside","is outside range"));
    node.appendChild(option("lte","is at most"));
    node.appendChild(option("gte","is at least"));
    node.appendChild(option("is","is"));
    node.appendChild(option("notis","is not"));
  } else if (cat == "date") {
    node.id = "range";
    node.appendChild(option("inside","is within range"));
    node.appendChild(option("outside","is outside range"));
    node.appendChild(option("before","is before"));
    node.appendChild(option("after","is after"));
    node.appendChild(option("last","is in the last"));
    node.appendChild(option("nolast","is not in the last"));
  }
  return node;
}

function change_kind(select) {
  var option = select.childNodes[select.selectedIndex];
  var newcat = category(option.getAttribute("value"));
  var oldcat = select.id;
  if (oldcat == newcat) return;
  // We are changing categories, so we need new stuff.
  var listitem = select.parentNode;
  listitem.removeChild(select.nextSibling);
  listitem.removeChild(select.nextSibling);
  if (newcat == "bool") {
    var btn = button("+","add(this);")
    listitem.appendChild(btn);
    listitem.appendChild(document.createElement("ul"));
    add(btn);  // Add an item to the newly created list.
  } else {
    var rulesel = rule_select(newcat);
    listitem.appendChild(rulesel);
    var rule = rulesel.firstChild.getAttribute("value");
    listitem.appendChild(field_span(auspice(newcat,rule)));
  }
  select.id = newcat;
}

function change_rule(select) {
  var cat = select.previousSibling.id;
  var option = select.childNodes[select.selectedIndex];
  var newausp = auspice(cat,option.getAttribute("value"));
  var oldausp = select.id;
  if (oldausp == newausp) return;
  // We are changing auspices, so we need new stuff.
  var listitem = select.parentNode;
  listitem.removeChild(select.nextSibling);
  listitem.appendChild(field_span(newausp));
  select.id = newausp;
}

function textbox(size) {
  var node = document.createElement("input");
  node.setAttribute("type","text");
  node.setAttribute("size",size);
  return node;
}

function field_span(ausp) {
  var span = document.createElement("span");
  span.className = "field";
  if (ausp == "str") span.appendChild(textbox("30"));
  else if (ausp == "one") span.appendChild(textbox("14"));
  else if (ausp == "range") {
    span.appendChild(textbox("14"));
    span.appendChild(textbox("14"));
  } else if (ausp == "udate") {
    span.appendChild(textbox("5"));
    var select = document.createElement("select");
    select.appendChild(option("hour","hours"));
    select.appendChild(option("day","days"));
    select.appendChild(option("week","weeks"));
    select.appendChild(option("month","months"));
    select.appendChild(option("year","years"));
    span.appendChild(select);
  }
  return span;
}

function category(kind) {
  if (kind == "title" || kind == "album" || kind == "artist") return "str";
  else if (kind == "time" || kind == "track") return "int";
  else if (kind == "date_added" || kind == "last_queued") return "date";
  else if (kind == "and" || kind == "or" || kind == "nand" || kind == "nor") {
    return "bool";
  } else return "nix";
}

function auspice(cat,rule) {
  if (cat == "str") return "str";
  else if (cat == "int") {
    if (rule == "is" || rule == "notis" || rule == "lte" || rule == "gte") {
      return "one";
    } else if (rule == "inside" || rule == "outside") return "range";
  }
  else if (cat == "date") {
    if (rule == "before" || rule == "after") return "one";
    else if (rule == "inside" || rule == "outside") return "range";
    else if (rule == "last" || rule == "nolast") return "udate"
  }
  return "nix";
}

function criterion() {
  var listitem = document.createElement("li");
  listitem.appendChild(button("\u2212","remove(this);"));
  listitem.appendChild(kind_select());
  listitem.appendChild(rule_select("str"));
  listitem.appendChild(field_span("str"));
  return listitem;
}

function remove(button) {
  var listitem = button.parentNode;
  listitem.parentNode.removeChild(listitem);
}

function add(button) {
  button.nextSibling.appendChild(criterion());
}

function subgather(item,prefix) {
  var kindsel = item.firstChild.nextSibling;
  kindsel.setAttribute("name",prefix);
  if (kindsel.id == "bool") {
    prefix += "_"
    var kids = kindsel.nextSibling.nextSibling.childNodes;
    for (var i = 0; i < kids.length; i++) subgather(kids[i], prefix+i);
  } else {
    var rulesel = kindsel.nextSibling;
    rulesel.setAttribute("name",prefix+"_r");
    prefix += "_f"
    var flds = rulesel.nextSibling.childNodes;
    for (var i = 0; i < flds.length; i++) flds[i].setAttribute("name",prefix+i)
  }
}

function gather() {
  subgather(document.getElementById("root"),"k");
}
