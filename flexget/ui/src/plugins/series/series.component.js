(function () {
  'use strict';

  angular
    .module('flexget.plugins.series')
    .component('seriesView', {
      templateUrl: 'plugins/series/series.tmpl.html',
      controllerAs: 'vm',
      controller: seriesController,
    });

  function seriesController($http, $mdDialog) {
    var vm = this;

    var options = {
      page: 1,
      page_size: 10,
      in_config: 'all',
      lookup: 'tvdb',
      sort_by: 'show_name'
    }

    vm.searchTerm = "";

    function getSeriesList() {
      $http.get('/api/series/', { params: options })
      .success(function(data) {
        vm.series = data.shows;

        //Set vars for pagination
        vm.currentPage = data.page;
        vm.totalShows = data.total_number_of_shows;
        vm.pageSize = data.page_size;
      });
    }

    vm.forgetShow = function(show) {
       var confirm = $mdDialog.confirm()
      .title('Confirm forgetting show.')
      .htmlContent("Are you sure you want to completely forget <b>" + show.show_name + "</b>?")
      .ok("Forget")
      .cancel("No");

      $mdDialog.show(confirm).then(function() {
        $http.delete('/api/series/' + show.show_id)
        .success(function(data) {
          var index = vm.series.indexOf(show);
          vm.series.splice(index, 1);
        })
        .error(function(error) {
          var errorDialog = $mdDialog.alert()
          .title("Something went wrong")
          .htmlContent("Oops, something went wrong when trying to forget <b>" + show.show_name + "</b>:\n" + error.message)
          .ok("Ok");

          $mdDialog.show(errorDialog);
        })
      });
    }

    //Call from the pagination to update the page to the selected page
    vm.updateListPage = function(index) {
      options.page = index;

      getSeriesList();
    }

    vm.search = function() {
      $http.get('/api/series/search/' + vm.searchTerm, { params: options })
      .success(function(data) {
        vm.series = data.shows;
      });
    }

    

    //Load initial list of series
    getSeriesList();
  }

})();
