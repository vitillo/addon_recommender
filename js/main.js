"use strict";

var priors = null;
var likelihood = null;

function load(data) {
  priors = data['priors'];
  likelihood = data['likelihood'];
}

function setupAutocomplete() {
  var i =0;
  var suggestions = []

  for (var prior in priors) {
    suggestions.push({id: prior, text: prior})
  }

  query = $('.select2, .select2-multiple').select2({ placeholder: 'Your Firefox Addons',
                                                     data: suggestions,
                                                     multiple: true,
                                                     openOnEnter: false,
                                                     closeOnSelect: true})
                                          .on("change", function(e) { inference(e.val) })
  $('#search').click(search);
  inference(query.select2('val')); // show priors
}

function inference(addons) {
  var updatedPriors = {}

  for (var prior in priors) {
    var score = priors[prior];

    for (var i = 0; i < addons.length; i++) {
      var addon = addons[i];
      var term = 0;

      if(likelihood[prior]) {
        var lh = likelihood[prior];
        var term = lh[addon] ? lh[addon] : 0;
        score += term;
      }
    }

    updatedPriors[prior] = score;
  }

  for (var i = 0; i < addons.length; i++) {
    updatedPriors[addons[i]] = -Number.MAX_VALUE;
  }

  var sorted = getSortedKeys(updatedPriors);
  var table = $('#recommendations');
  var rows = ""

  $("#recommendations tr").remove();
  for (var i = 0; i < 10; i++) {
    rows += "<tr><td>" + sorted[i] + "</td></tr>";
  }
  table.append(rows);
}

function getSortedKeys(obj) {
  var keys = [];

  for (var key in obj) {
    keys.push(key);
  }

  return keys.sort(function(a,b){return obj[b]-obj[a]});
}

$.getJSON('data/probabilities.json', function(data) {
  load(data);
  setupAutocomplete()
});
