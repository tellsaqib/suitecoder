var mainApp = angular.module('mainApp', ['dateFilters', 'ngAnimate', 'angularTreeview']);
mainApp.factory('accountNumber', [function() {
        var accountNumber = null;
        return {
            get: function() {
                return accountNumber;
            },
            set: function(numer) {
                accountNumber = numer;
            }
        };
    }]);

angular.module('dateFilters', []).filter('toDateView', function() {
    return function(input) {
        return new Date(parseInt(input) * 1000).toLocaleString();
    };
});

mainApp.controller('mainCtrl', function($scope, $http, $rootScope, accountNumber, $sce, $filter) {
    $scope.richCodeEditor = true;
    $scope.diffMode = 0;
    $scope.fileOrder = 'name';
    $scope.openedFiles = {};

    $rootScope.openFile = function(name, type, id, url, postData, breadCrumbs) {

        if (!$scope.openedFiles[type + id]) {//Check if file is already loaded
            $scope.openedFiles[type + id] = {//Load file
                name: name,
                type: type,
                id: id,
                postData: postData,
                content: '',
                saveHistory: true,
                msg: 'Loading content...',
                breadCrumbs: breadCrumbs,
                contentLoaded: false
            };
            $http.post(url, postData).success(function(data) {
                if (data.status) {
                    $scope.openedFiles[type + id].content = data.content;
                    $scope.openedFiles[type + id].contentLoaded = true;
                    $scope.openedFiles[type + id].msg = 'Content Loaded.';
                    window.setTimeout($scope.tabShownHandler, 500);
                } else {
                    $scope.openedFiles[type + id].msg = data.message;
                }
            }).error(function() {
                $scope.openedFiles[type + id].msg = 'An error occurred while loading the content. Please try again later.';
            });
        }
        //Finally open the tab
        window.setTimeout("$('#tabs a[href=\"#" + type + id + "\"]').tab('show')", 300);
    };

    $scope.keyHandler = function(e, file) {
        if (e.keyCode === 83 && (navigator.platform.match("Mac") ? e.metaKey : e.ctrlKey)) {
            e.preventDefault();
            $scope.saveFile(file);
        } else {
            return true;
        }
    };

    $scope.saveFile = function(file, tabId) {
        file.msg = 'Saving file...';
        var postData = angular.copy(file.postData);
        postData.save_history = file.saveHistory;
        postData.content = file.content;
        postData.file_id = file.id;
        $http.post('/' + file.type + '?action=update_file', postData).success(function() {
            file.msg = 'File saved.';
        }).error(function() {
            file.msg = 'Unable to save file.';
        });
    };
    $scope.closeFile = function(id) {
        delete $scope.openedFiles[id];
        $('#tabs a:first').tab('show');
    };
    $scope.listHistory = function(file, tabId) {
        file.diffMode = true;
        file.historyList = [];
        file.msg = 'Laoding history list ...';
        var fileId = file.id;
        if (file.type === 'account')
            fileId = accountNumber.get() + '_' + fileId;

        $http.get('/history?action=getList&fileid=' + fileId).success(function(data) {
            if (data.status) {
                file.historyList = data.records;
                file.msg = 'History list loaded. Click on any date to load diff.';
            } else {
                file.msg = data.message;
            }
        }).error(function() {
            file.msg = 'Unable to load history';
        });
    };
    $scope.viewEditor = function(file) {
        file.diffMode = false;
        file.msg = '';
    };
    $scope.loadDiff = function(revision, tabId, event) {
        $('.history-label').removeClass('selected');
        $(event.target).addClass('selected');
        $scope.openedFiles[tabId].msg = 'Loading diff ...';
        $scope.openedFiles[tabId].diffText = '';
        $scope.openedFiles[tabId].diffWidgetHTML = $sce.trustAsHtml('');
        $http.get('/history?action=getContent&key=' + revision.key).success(
                function(data) {
                    if (data.status) {
                        $scope.openedFiles[tabId].diffText = data.content;
                        var base = difflib.stringAsLines($scope.openedFiles[tabId].content);
                        var newtxt = difflib.stringAsLines($scope.openedFiles[tabId].diffText);
                        var sm = new difflib.SequenceMatcher(base, newtxt);
                        var opcodes = sm.get_opcodes();
                        var tableElem = diffview.buildView({
                            baseTextLines: base,
                            newTextLines: newtxt,
                            opcodes: opcodes,
                            baseTextName: " Current File",
                            newTextName: " File History @ " + $filter('toDateView')(revision.time),
                            viewType: parseInt($scope.diffMode)
                        });
                        var tempElem = document.createElement('div');
                        tempElem.appendChild(tableElem.cloneNode(true));
                        $scope.openedFiles[tabId].diffWidgetHTML = $sce.trustAsHtml(tempElem.innerHTML);
                        $scope.openedFiles[tabId].msg = 'Diff loaded.';
                    } else {
                        $scope.openedFiles[tabId].msg = data.message;
                    }
                }).error(
                function() {
                    $scope.openedFiles[tabId].msg = 'Unable to load diff.';
                });
    };
    $scope.updateTag = function(revision) {
        revision.saving = true;
        $http.post('/history?action=saveTag', {key: revision.key, tag: revision.tag}).finally(function() {
            revision.saving = false;
        });
    };
    $scope.tabShownHandler = function() {
        if ($scope.richCodeEditor && $('textarea:visible').length) {
            var taElem = document.getElementById($('textarea:visible').attr('id'));
            var tabId = $('textarea:visible').attr('data-tabid');
            $scope.openedFiles[tabId].cmObject = CodeMirror.fromTextArea(taElem, {
                mode: "javascript",
                lineNumbers: true,
                autofocus: true,
                'onChange': function(from) {
                    $scope.openedFiles[tabId].content = from.getValue();
                },
                extraKeys: {
                    "Ctrl-Space": function(cm) {
                        CodeMirror.simpleHint(cm, CodeMirror.javascriptHint);
                    }
                }
            });
        }
    };

    //Show textarea/rich code editor as per user preference
    $scope.UpdateCodeEditor = function() {
        if (!$scope.richCodeEditor) {
            for (var tabId in $scope.openedFiles) {
                if ($scope.openedFiles[tabId].cmObject) {
                    $scope.openedFiles[tabId].cmObject.toTextArea();
                    $scope.openedFiles[tabId].cmObject = null;
                }
            }
        } else {
            $scope.tabShownHandler();
        }
    };

    $('#tabs').on('shown.bs.tab', 'a', $scope.tabShownHandler);
});
mainApp.controller('accountCtrl', function($scope, $rootScope, $http, accountNumber, $sce) {
    $scope.creds = {};
//    accountCreds.update('role', "12");
//    accountCreds.update('role_id', 3);
//    accountCreds.update('webservice_url', "https://webservices.na1.netsuite.com");
    $scope.loginStatus = 0;
    $scope.loginMsg = 'Enter your Netsuite credentails to edit files on  your Netsuite account.';
    $scope.folders = [];
    $scope.accountFiles = null;
    $scope.selectedFolder = null;

    $scope.roleChange = function() {
        if (typeof $scope.role !== 'undefined') {
            $scope.creds.account_id = $scope.roles[$scope.role].account.internalId;
            $scope.creds.role_id = $scope.roles[$scope.role].role.internalId;
            $scope.creds.webservice_url = $scope.roles[$scope.role].dataCenterURLs.webservicesDomain;
            accountNumber.set($scope.creds.account_id);
        }
    };

    $scope.$watch('role', $scope.roleChange);

    $scope.getRoles = function() {
        if ($scope.loginForm.$valid === false) {
            $scope.loginMsg = 'Enter the credentials correctly.';
            return;
        }
        $scope.loginMsg = 'Logging in ...';
        $scope.inProgress = true;
        $http.post('/account?action=login', $scope.creds).success(function(data) {
            if (data.error) {
                $scope.loginMsg = data.error.message;
            } else {
                $scope.roles = data;
                $scope.role = 0;
                $scope.roleChange();

                if ($scope.roles.length === 1) {
                    $scope.getFolders();
                } else {
                    $scope.loginStatus = 1;
                    $scope.loginMsg = 'Please select a role and click proceed.';
                }
            }
        }).error(function() {
            $scope.loginMsg = 'Unable to login. Please try again';
        }).finally(function() {
            $scope.inProgress = false;
        });
    };

    $scope.getFolders = function() {
        $scope.tempfolderSelectOptions = '<option value="">-- Select a folder --</option>';
        $scope.inProgress = true;
        $http.post('account?action=getfolders', $scope.creds).success(function(data) {
            $scope.loginMsg = '';
            $scope.msg = 'Click any folder to browse its files.';
            if (data.status) {
                $scope.loginStatus = 2;
                for (var i in data.result)
                    if (data.result[i]['parent'] === 0) {
                        var folder = data.result[i];
                        $scope.tempfolderSelectOptions += '<option value="' + folder.id + '">' + folder.name + '</option>';
                        folder.subFolders = $scope.handleFolder(data.result[i], data.result, '-- ');
                        $scope.folders.push(folder);

                    }
                $scope.folderSelectOptions = $sce.trustAsHtml($scope.tempfolderSelectOptions);
            } else {
                $scope.loginMsg = data.message ? data.message : 'Unable to load folders. Please try again.';
            }

        }).error(function() {
            $scope.msg = 'An error occurred. Please try again.';
        }).finally(function() {
            $scope.inProgress = false;
        });

    };
    $scope.handleFolder = function(folder, list, optionPrefix) {
        var subFolders = [];
        for (var i in list)
            if (list[i]['parent'] === folder['id']) {
                var temp = list[i];
                $scope.tempfolderSelectOptions += '<option value="' + folder.id + '">' + optionPrefix + temp.name + '</option>';
                temp.subFolders = $scope.handleFolder(list[i], list, optionPrefix + '-- ');
                subFolders.push(list[i]);
            }
        return subFolders;
    };

    $scope.addFile = function() {
        $scope.msg = 'Creating file...';
        $scope.inProgress = true;
        $http.post('account?action=addfile' + '&filename=' + $scope.newFileName + '&folderid=' + $scope.newFileFolder, $scope.creds).success(
                function(data) {
                    if (data.status) {
                        $scope.msg = 'File added.';
                        if ($scope.selectedFolder.id == $scope.newFileFolder) {
                            $scope.files.push(data.file);
                        }
                    }
                    else
                        $scope.msg = data.message;
                }).error(function() {
            $scope.msg = 'An error occurred. Please try again.';
        }).finally(function() {
            $scope.inProgress = false;
        });
    };

    /*
     Called when a folder in folder tree is clicked
     */
    $scope.$watch('tree.currentNode', function() {
        $scope.selectedFolder = $scope.tree.currentNode;
        if ($scope.selectedFolder) {
            $scope.accountFiles = [];
            $scope.msg = 'Loading Files ...';
            $http.post('account?action=getfiles' + '&folderid=' + $scope.selectedFolder.id, $scope.creds)
                    .success(function(data) {
                        if (data.status) {
                            $scope.msg = 'Files loaded.';
                            $scope.accountFiles = data.files;
                        }
                    })
                    .error(function() {
                        $scope.msg = 'Unable to load File List.';
                    });
        }

    });

    $scope.openFile = function(file) {
        var crumbs = ['Account Files'];
        try {
            var grandParent = $('span:first', $('span.selected:visible').parent().parent().parent().parent()).text();
            if (grandParent)
                crumbs.push(grandParent);
        } catch (exc) {
            ;
        }
        crumbs.push($('span.selected:visible').text());

        $rootScope.openFile(file.name, 'account', file.id, '/account?action=loadFile&id=' + file.id, $scope.creds, crumbs);
    };

});
mainApp.controller('localCtrl', function($scope, $http, $rootScope) {
    $scope.msg = 'Loading folders...';
    $scope.formView = 0;
    $http.get('local?action=get_folders').success(function(data) {
        if (data.status) {
            $scope.folders = data.folders;
            $scope.msg = 'Select any folder to view its files.';
        }
        else
            $scope.msg = 'Unable to load folders';
    }).error(function() {
        $scope.msg = 'Unable to load folders';
    });
    $scope.addFolder = function() {
        $scope.msg = 'Adding Folder';
        $scope.inProgress = true;
        $http.get('local?action=add_folder&name=' + $scope.newFolderName).success(function(data) {
            if (data.status) {
                $scope.newFolderName = '';
                $scope.formView = 0;
                $scope.folders.push(data.folder);
            }
            $scope.msg = data.message;
        }).error(function(data) {
            $scope.msg = 'An error occurred. Please try again.';
        }).finally(function() {
            $scope.inProgress = false;
        });
    };

    $scope.renameFolder = function(folder) {
        var newFolderName = window.prompt('Enter new name for folder', folder.name);
        if (newFolderName) {
            $scope.msg = 'Renaming folder ...';
            $http.get('local?action=rename_folder&name=' + newFolderName + '&folder=' + folder.key).success(function(data) {
                if (data.status) {
                    folder.name = newFolderName;
                    $scope.msg = 'Folder name updated.';
                } else {
                    $scope.msg = data.message;
                }
            }).error(function() {
                $scope.msg = 'Unable to rename folder';
            });
        }
    };

    $scope.deleteFolder = function(folder) {
        if (window.confirm('Folder "' + folder.name + '" will be deleted.')) {
            $scope.msg = 'Deleting folder ...';
            $http.get('local?action=delete_folder&folder=' + folder.key).success(function(data) {
                if (data.status) {
                    $scope.msg = 'Folder deleted.';
                    for (var i in $scope.folders)
                        if ($scope.folders[i].key === folder.key)
                            $scope.folders.splice(i, 1);
                } else {
                    $scope.msg = data.message;
                }

            }).error(function() {
                $scope.msg = 'Unable to delete folder';
            });
        }
    };

    $scope.addFile = function() {
        $scope.msg = 'Adding file...';
        $scope.inProgress = true;
        $http.get('local?action=add_file&name=' + $scope.newFileName + '&folder=' + $scope.newFileFolder).success(function(data) {
            if (data.status) {
                if ($scope.newFileFolder === $scope.selectedFolder.key)
                    $scope.files.push(data.file);
                $scope.newFileName = '';
                $scope.newFolderName = '';
                $scope.msg = data.message;
                $scope.msg = 'File added.';
            }
        }).error(function() {
            $scope.msg = 'Unable to add file';
        }).finally(function() {
            $scope.inProgress = false;
        });
    };

    $scope.getFiles = function(folder, event) {
        $('.local-folder-label').removeClass('selected');
        $(event.target).addClass('selected');
        $scope.selectedFolder = folder;
        $scope.msg = 'Loading Files';
        $scope.files = [];
        $http.get('local?action=get_files&folder=' + folder.key).success(function(data) {
            if (data.status) {
                $scope.files = data.files;
                $scope.msg = 'Files loaded.';
            }
        });
    };
    $scope.openFile = function(file) {
        $rootScope.openFile(file.name, 'local', file.id, '/local?action=load_file&id=' + file.id, {}, ['My Files', $('.local-folder-label.selected').text()]);
    };

    $scope.deleteFile = function(file) {
        if (!confirm('File "' + file.name + '" will be deleted.'))
            return;
        $scope.msg = 'Deleting file ...';
        $http.get('local?action=delete&file=' + file.id).success(function(data) {
            if (data.status) {
                $scope.msg = 'File deleted';
                for (var i in $scope.files)
                    if ($scope.files[i].id == file.id)
                        $scope.files.splice(i, 1);
            } else {
                $scope.msg = data.message;
            }
        }).error(function() {
            $scope.msg = 'An error occurred while deleting the file.';
        });
    };
});

$(document).ready(function() {

    window.onbeforeunload = function() {
//return "Any unsaved data will be lost.";
    };

    $('.dropdown-menu').on('click', function(e) {
        e.stopPropagation();
    });
});