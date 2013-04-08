(function($) {
	$.fn.TagDynamic = function(opts) {
		var options = $.extend({}, $.fn.TagDynamic.defaults, opts);
		return this.each(function() {
			var $dom = $(this);
			new TagDynamicClass(options, $dom).init();
		});
	};
	$.fn.TagDynamic.defaults = {
		container_class: '',
		button_str: '添加',
		autocomplete_serveice: '',
		data_list: []
	};

	function TagDynamicClass(options, $dom) {
		this.options = options;
		this.$dom = $dom;
	};
	$.extend(TagDynamicClass.prototype, {
		init: function() {
			var me = this;
			var options = this.options,
				$dom = this.$dom;
			if (this.options.container_class) {
				$dom.wrap('<div class="tag_dynamic_container ' + options.container_class + '"></div>');
			} else {
				$dom.wrap('<div class="tag_dynamic_container"></div>');
			}
			this.root = $dom.parent('.tag_dynamic_container');
			this.button = $('<button class="png_bg">' + options.button_str + '</button>').insertAfter($dom);
			this.list = $('<ol class="tag_dynamic_list"></ol>').appendTo(this.root);
			var data_list_len = options.data_list.length;
			if (data_list_len > 0) {
				var ipt_name = $dom.attr('name');
				if (!ipt_name) {
					alert('input name needed!')
					return false
				}
				var html = '';
				for (var i = 0; i < data_list_len; i++) {
					html += '<li><input type="checkbox" checked="checked" name="' + (ipt_name + '[]') + '" value="' + options.data_list[i].value + '">';
					html += '<label id="labelid">' + options.data_list[i].label + '</label>';
					html += '<a href="javascript:void(0)" class="remove">x</a></li>';
					html += '</li>';
				} 
				$(html).appendTo(this.list).find('a.remove').click(function() {
					$(this).parent().remove();
				})
			}
			
    	
			this.button.click(function() {
				var label = $dom.val();
				if (label == '') {
					$dom.focus();
				} else {
					//alert(label);
					me.add_item(label)
				}
				return false
			})
			if (options.autocomplete_service){
				$dom.autocomplete(options.autocomplete_service, {
					scrollHeight: 400,
					selectFirst: false,
					cacheLength: 0,
					formatItem: function(item) {
						return item.label;
					},
					formatMatch: function(data, i, total) {
						return data.label;
					},
					formatResult: function(data) {
						return data.label;
					},
					parse: function(data) {
						var parsed = '';
						if (data) {
							var list = eval('(' + data + ')'),
								parsed = [];
							for (var i = 0, j = list.length; i < j; i++) {
								parsed[i] = {
									data: list[i],
									value: list[i].value,
									label: list[i].label
								};
							}
						}
						return parsed
					}
				}).result(function(event, item) {
					me.add_item(item.label, item.value);
					$dom.val('').focus();
				})
			}
		},
		add_item: function(label, value) {
			if (!value) {
				value = label;
			}
			var flag = true;
			this.list.find('label').each(function() {
				if ($(this).text() == label) {
					flag = false
					return
				}
			})
			if (flag) {
				var $remove = $('<a href="javascript:;" class="remove">x</a>').click(function() {
					$(this).parent().remove();
				})
				var ipt_name = this.$dom.attr('name');
				if (!ipt_name) {
					alert('input name needed!')
					return false
				}
				//$('<li/>').append('<input type="checkbox" checked="checked" name="' + (ipt_name + '[]') + '" value="' + value + '">').append('<label id='+label+'>' + label + '</label>').append($remove).appendTo(this.list);
				
				$('<li/>')
					.append('<input type="checkbox" checked="checked" name="'+(ipt_name+'[]')+'" value="'+value+'">')
					.append('<label id='+label+'>'+ label +'</label>')
					.append($remove)
					.appendTo(this.list);
					
			  $('#'+label+'').click(function() {
					alert('dd:'+$(this).html('dsd'));
    		});
    		
    		this.$dom.val('').focus();
			} else {
				alert('不能添加重复项')
				this.$dom.focus().get(0).select()
			}
		}
	});
})(jQuery);