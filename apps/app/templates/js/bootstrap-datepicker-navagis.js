/* =========================================================
 * bootstrap-datepicker.js 
 * http://www.eyecon.ro/bootstrap-datepicker
 * =========================================================
 * Copyright 2012 Stefan Petre
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 * ========================================================= */
 
 /*
	Modified by Yudistira Purwatama and Jhalley de Castro for use by Navagis.
	
	Added ability to programatically set the view limit of date to month, year, and date on the fly.
 
 */
 
!function( $ ) {
	
	// Picker object
	
	var Datepicker = function(element, options){

        this.weekHighlight = false;
		this.element = $(element);
		this.format = DPGlobal.parseFormat(options.format||this.element.data('date-format')||'mm/dd/yyyy');
		this.picker = $(DPGlobal.template)
							.appendTo('body')
							.on({
								click: $.proxy(this.click, this)//,
								//mousedown: $.proxy(this.mousedown, this)
							});
		this.isInput = this.element.is('input');
		this.component = this.element.is('.date') ? this.element.find('.add-on') : false;
		
		if (this.isInput) {
			this.element.on({
				focus: $.proxy(this.show, this),
				//blur: $.proxy(this.hide, this),
				keyup: $.proxy(this.update, this)
			});
		} else {
			if (this.component){
				this.component.on('click', $.proxy(this.show, this));
			} else {
				this.element.on('click', $.proxy(this.show, this));
			}
		}
	
		this.minViewMode = options.minViewMode||this.element.data('date-minviewmode')||0;
		if (typeof this.minViewMode === 'string') {
			switch (this.minViewMode) {
				case 'months':
					this.minViewMode = 1;
					break;
				case 'years':
					this.minViewMode = 2;
					break;
				default:
					this.minViewMode = 0;
					break;
			}
		}
		this.viewMode = options.viewMode||this.element.data('date-viewmode')||0;
		if (typeof this.viewMode === 'string') {
			switch (this.viewMode) {
				case 'months':
					this.viewMode = 1;
					break;
				case 'years':
					this.viewMode = 2;
					break;
				default:
					this.viewMode = 0;
					break;
			}
		}
		this.startViewMode = this.viewMode;
		this.weekStart = options.weekStart||this.element.data('date-weekstart')||0;
		this.weekEnd = this.weekStart === 0 ? 6 : this.weekStart - 1;
		this.onRender = options.onRender;
		this.fillDow();
		this.fillMonths();
		this.update();
		this.showMode();
	};
	
	Datepicker.prototype = {
		constructor: Datepicker,

        setViewLimitYear: function(e){
            this.picker.remove();
		    this.picker = $(DPGlobal.template)
							.appendTo('body')
							.on({
								click: $.proxy(this.click, this)//,
								//mousedown: $.proxy(this.mousedown, this)
							});
            this.weekHighlight = false;
            this.viewMode = 2;
            this.minViewMode = 2;
		    this.format = DPGlobal.parseFormat(this.element.data('date-format')||'yyyy');
		    this.startViewMode = this.viewMode;
			this.fillDow();
		    this.fillMonths();
		    this.update();
		    this.showMode();
        },

        setViewLimitMonth: function(e){
			this.picker.remove();
		    this.picker = $(DPGlobal.template)
							.appendTo('body')
							.on({
								click: $.proxy(this.click, this)//,
								//mousedown: $.proxy(this.mousedown, this)
							});
            this.weekHighlight = false;
            this.viewMode = 1;
            this.minViewMode = 1;
		    this.format = DPGlobal.parseFormat(this.element.data('date-format')||'mm/yyyy');
		    this.startViewMode = this.viewMode;
			this.fillDow();
			this.fillMonths();
		    this.update();
		    this.showMode();
        },

        setViewLimitDay: function(e){
            this.picker.remove();
		    this.picker = $(DPGlobal.template)
							.appendTo('body')
							.on({
								click: $.proxy(this.click, this)//,
								//mousedown: $.proxy(this.mousedown, this)
							});
            this.weekHighlight = false;
            this.viewMode = 0;
            this.minViewMode = 0;
		    this.format = DPGlobal.parseFormat(this.element.data('date-format')||'dd/mm/yyyy');
		    this.startViewMode = this.viewMode;
			this.fillDow();
		    this.fillMonths();
		    this.update();
		    this.showMode();
        },
        setViewLimitWeek: function(e){
            this.picker.remove();
		    this.picker = $(DPGlobal.template)
							.appendTo('body')
							.on({
								click: $.proxy(this.click, this)//,
								//mousedown: $.proxy(this.mousedown, this)
							});
            this.weekHighlight = true;
            this.weekEnd = this.weekStart === 0 ? 6 : this.weekStart - 1;
            this.viewMode = 0;
            this.minViewMode = 0;
		    this.format = DPGlobal.parseFormat(this.element.data('date-format')||'dd/mm/yyyy');
		    this.startViewMode = this.viewMode;
			this.fillDow();
		    this.fillMonths();
		    this.update();
		    this.showMode();
        },
		show: function(e) {
			this.picker.show();
			this.height = this.component ? this.component.outerHeight() : this.element.outerHeight();
			this.place();
			$(window).on('resize', $.proxy(this.place, this));
			if (e ) {
				e.stopPropagation();
				e.preventDefault();
			}
			if (!this.isInput) {
			}
			var that = this;
			$(document).on('mousedown', function(ev){
				if ($(ev.target).closest('.datepicker').length == 0) {
					that.hide();
				}
			});
			this.element.trigger({
				type: 'show',
				date: this.date
			});
		},
		
		hide: function(){
			this.picker.hide();
			$(window).off('resize', this.place);
			this.viewMode = this.startViewMode;
			this.showMode();
			if (!this.isInput) {
				$(document).off('mousedown', this.hide);
			}
			//this.set();
			this.element.trigger({
				type: 'hide',
				date: this.date
			});
		},
		
		set: function() {
            if (! this.weekHighlight )
            {
                var formated = DPGlobal.formatDate(this.date, this.format);
            }
            else
            {
                var formated = DPGlobal.formatDate(this.date_start_of_week, this.format) + ' - ' + DPGlobal.formatDate(this.date_end_of_week, this.format);
            }            
			if (!this.isInput) {
				if (this.component){
					this.element.find('input').prop('value', formated);
				}
				this.element.data('date', formated);
			} else {
				this.element.prop('value', formated);
			}
		},
        
        destroy: function(e) {
            this.picker.remove();
        },
		
		setValue: function(newDate) {
			if (typeof newDate === 'string') {
				this.date = DPGlobal.parseDate(newDate, this.format);
			} else {
				this.date = new Date(newDate);
			}
			this.set();
			this.viewDate = new Date(this.date.getFullYear(), this.date.getMonth(), 1, 0, 0, 0, 0);
			this.fill();
		},
		
        getValue: function()
        {
            if (this.weekHighlight)
            {
                return { 'type' : 'week', 'epoch' : this.date.valueOf(), 'date_day' : this.date_start_of_week.getDate(), 'date_month' : this.date_start_of_week.getMonth() + 1, 'date_year' : this.date_start_of_week.getFullYear() };
            }
            
            if (this.viewMode == 0)
            {
                return { 'type' : 'day', 'epoch' : this.date.valueOf() ,'date_day' : this.date.getDate(), 'date_month' : this.date.getMonth() + 1, 'date_year' : this.date.getFullYear() };

            }
            
            if (this.viewMode == 1)
            {
                return { 'type' : 'month', 'date_month' : this.date.getMonth() + 1, 'date_year' : this.date.getFullYear() };
            }
            
            if (this.viewMode == 2)
            {
                return { 'type' : 'year', 'date_year' : this.date.getFullYear() };
            }
        },

		place: function(){
			var offset = this.component ? this.component.offset() : this.element.offset();
			this.picker.css({
				top: offset.top + this.height,
				left: offset.left
			});
		},

		update: function(newDate){
			this.date = DPGlobal.parseDate(
				typeof newDate === 'string' ? newDate : (this.isInput ? this.element.prop('value') : this.element.data('date')),
				this.format
			);
            this.date_start_of_week = new Date(this.date.valueOf());
            this.date_start_of_week.setDate(this.date.getDate() - (( this.date.getDay() - this.weekStart + 7) % 7 ));
            this.date_end_of_week = new Date(this.date_start_of_week.valueOf());
            this.date_end_of_week.setDate( this.date_start_of_week.getDate() + 6 );
			this.viewDate = new Date(this.date.getFullYear(), this.date.getMonth(), 1, 0, 0, 0, 0);
			this.fill();
		},
		
		fillDow: function(){
			var dowCnt = this.weekStart;
			var html = '<tr>';
			while (dowCnt < this.weekStart + 7) {
				html += '<th class="dow">'+DPGlobal.dates.daysMin[(dowCnt++)%7]+'</th>';
			}
			html += '</tr>';
			this.picker.find('.datepicker-days thead').append(html);
		},
		fillMonths: function(){
			var html = '',
				i = 0,
				now = new Date(),
				currentValueYear;

			var nowYear = now.getFullYear(),
				nowMonth = now.getMonth();

			if(this.date) currentValueYear = this.date.getFullYear();

			while (i < 12) {
				if(currentValueYear) {
					if(currentValueYear < nowYear) {
						html += '<span class="month">' + DPGlobal.dates.monthsShort[i++] + '</span>';
					} else {
						html += '<span class="month' + (i > nowMonth ? ' disabled' : '') + '">' + DPGlobal.dates.monthsShort[i++] + '</span>';
					}
				} else {
					html += '<span class="month">' + DPGlobal.dates.monthsShort[i++] + '</span>';
				}
			}
			this.picker.find('.datepicker-months td').append(html);
		},

		fill: function() {
			var d = new Date(this.viewDate),
				year = d.getFullYear(),
				month = d.getMonth(),
				currentDate = this.date.valueOf();

			var startDataDate = {year: 2015};
			var currentDate = new Date();
			var currentYear = currentDate.getFullYear();

            //for week highlight calculation : yudi.
            // var selected_start_of_week = new Date(this.date.valueOf());
            // selected_start_of_week.setDate(this.date.getDate() - (( this.date.getDay() - this.weekStart + 7) % 7 ));
            // var selected_end_of_week = new Date(selected_start_of_week.valueOf());
            // selected_end_of_week.setDate( selected_start_of_week.getDate() + 6 );

 			this.picker.find('.datepicker-days th:eq(1)')
						.text(DPGlobal.dates.months[month]+' '+year);
			var prevMonth = new Date(year, month-1, 28,0,0,0,0),
				day = DPGlobal.getDaysInMonth(prevMonth.getFullYear(), prevMonth.getMonth());
			prevMonth.setDate(day);
			prevMonth.setDate(day - (prevMonth.getDay() - this.weekStart + 7)%7);
			var nextMonth = new Date(prevMonth);
			nextMonth.setDate(nextMonth.getDate() + 42);
			nextMonth = nextMonth.valueOf();
			var html = [];
			var clsName,
				prevY,
				prevM,
                m_week_start,
                m_week_end,
                weekClsName;

			while(prevMonth.valueOf() < nextMonth) {

                if (prevMonth.getDay() === this.weekStart) {
                    m_week_start = new Date(prevMonth.valueOf()); m_week_start.setDate(prevMonth.getDate() - ( ( prevMonth.getDay() - this.weekStart + 7) % 7));
                    if (this.date_start_of_week && (m_week_start.valueOf() == this.date_start_of_week.valueOf()))
                    {
                        weekClsName = 'active';
                    }
                    else
                    {
                        weekClsName = '';
                    }

                    if (this.weekHighlight)
                    {
                        html.push('<tr class="datepicker-weekrow ' + weekClsName + '">');
                    }
                    else
                    {
                        html.push('<tr>');
                    }
				}
				clsName = this.onRender(prevMonth);
				prevY = prevMonth.getFullYear();
				prevM = prevMonth.getMonth();
				if ((prevM < month &&  prevY === year) ||  prevY < year) {
					clsName += ' old';
				} else if ((prevM > month && prevY === year) || prevY > year) {
					clsName += ' new';
				}
				if (prevMonth.valueOf() === currentDate) {
					clsName += ' active';
				}
				html.push('<td class="day '+clsName+'">'+prevMonth.getDate() + '</td>');
				if (prevMonth.getDay() === this.weekEnd) {
					html.push('</tr>');
				}
				prevMonth.setDate(prevMonth.getDate()+1);
			}
			this.picker.find('.datepicker-days tbody').empty().append(html.join(''));
			var currentYear = this.date.getFullYear();

			var months = this.picker.find('.datepicker-months')
						.find('th:eq(1)')
							.text(year)
							.end()
						.find('span').removeClass('active');
			if (currentYear === year) {
				months.eq(this.date.getMonth()).addClass('active');
			}

			html = '';
			year = parseInt(year/10, 10) * 10;
			var yearCont = this.picker.find('.datepicker-years')
								.find('th:eq(1)')
									//.text(year + '-' + (year + 9))
								.text(startDataDate.year + '-' + currentYear)
								.end()
								.find('td');
			year -= 1;
			for (var i = -1; i < 11; i++) {
				if(year < startDataDate.year || year > currentYear) {
					html += '<span class="year disabled"></span>';
				} else {
					html += '<span class="year' + (i === -1 || i === 10 ? ' old' : '') + (currentYear === year ? ' active' : '') + '">' + year + '</span>';
				}
				year += 1;
			}
			yearCont.html(html);
		},
		
		click: function(e) {
			e.stopPropagation();
			e.preventDefault();
			var target = $(e.target).closest('span, td, th');
			if (target.length === 1) {
				switch(target[0].nodeName.toLowerCase()) {
					case 'th':
						switch(target[0].className) {
							case 'switch':
								this.showMode(1);
								break;
							case 'prev':
							case 'next':
								if(this.viewDate < new Date()) {
									this.viewDate['set' + DPGlobal.modes[this.viewMode].navFnc].call(
											this.viewDate,
											this.viewDate['get' + DPGlobal.modes[this.viewMode].navFnc].call(this.viewDate) +
											DPGlobal.modes[this.viewMode].navStep * (target[0].className === 'prev' ? -1 : 1)
									);
									this.fill();
									this.set();
								}
								break;
						}
						break;
					case 'span':
						if (target.is('.month')) {
							var month = target.parent().find('span').index(target);
							this.viewDate.setMonth(month);
						} else {
							var year = parseInt(target.text(), 10)||0;
							this.viewDate.setFullYear(year);
						}
						if (this.viewMode !== 0) {
							this.date = new Date(this.viewDate);
							this.element.trigger({
								type: 'changeDate',
								date: this.date,
								viewMode: DPGlobal.modes[this.viewMode].clsName
							});
						}
						this.showMode(-1);
						this.fill();
						this.set();
						break;
					case 'td':
						if (target.is('.day') && !target.is('.disabled')){
							var day = parseInt(target.text(), 10)||1;
							var month = this.viewDate.getMonth();
							if (target.is('.old')) {
								month -= 1;
							} else if (target.is('.new')) {
								month += 1;
							}
							var year = this.viewDate.getFullYear();
							this.date = new Date(year, month, day,0,0,0,0);
                            this.date_start_of_week = new Date(this.date.valueOf());
                            this.date_start_of_week.setDate(this.date.getDate() - (( this.date.getDay() - this.weekStart + 7) % 7 ));
                            this.date_end_of_week = new Date(this.date_start_of_week.valueOf());
                            this.date_end_of_week.setDate( this.date_start_of_week.getDate() + 6 );
							this.viewDate = new Date(year, month, Math.min(28, day),0,0,0,0);
							this.fill();
							this.set();
							this.element.trigger({
								type: 'changeDate',
								date: this.date,
								viewMode: DPGlobal.modes[this.viewMode].clsName
							});
						}
						break;
				}
			}
		},
		
		mousedown: function(e){
			e.stopPropagation();
			e.preventDefault();
		},
		
		showMode: function(dir) {
			if (dir) {
				this.viewMode = Math.max(this.minViewMode, Math.min(2, this.viewMode + dir));
			}
			this.picker.find('>div').hide().filter('.datepicker-'+DPGlobal.modes[this.viewMode].clsName).show();
		}
	};
	
	$.fn.datepicker = function ( option, val ) {
		return this.each(function () {
			var $this = $(this),
				data = $this.data('datepicker'),
				options = typeof option === 'object' && option;
			if (!data) {
				$this.data('datepicker', (data = new Datepicker(this, $.extend({}, $.fn.datepicker.defaults,options))));
			}
			if (typeof option === 'string') data[option](val);
		});
	};

	$.fn.datepicker.defaults = {
		onRender: function(date) {
			return '';
		}
	};
	$.fn.datepicker.Constructor = Datepicker;
	
	var DPGlobal = {
		modes: [
			{
				clsName: 'days',
				navFnc: 'Month',
				navStep: 1
			},
			{
				clsName: 'months',
				navFnc: 'FullYear',
				navStep: 1
			},
			{
				clsName: 'years',
				navFnc: 'FullYear',
				navStep: 10
		}],
		dates:{
			days: ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
			daysShort: ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
			daysMin: ["Su", "Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"],
			months: ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"],
			monthsShort: ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
		},
		isLeapYear: function (year) {
			return (((year % 4 === 0) && (year % 100 !== 0)) || (year % 400 === 0))
		},
		getDaysInMonth: function (year, month) {
			return [31, (DPGlobal.isLeapYear(year) ? 29 : 28), 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month]
		},
		parseFormat: function(format){
			var separator = format.match(/[.\/\-\s].*?/),
				parts = format.split(/\W+/);
			if (!parts || parts.length === 0){
				throw new Error("Invalid date format.");
			}
            if (!separator)
            {
                separator = [];
            }

			return {separator: separator, parts: parts};
		},
		parseDate: function(date, format) {
			var parts = date.split(format.separator),
				date = new Date(),
				val;
			date.setHours(0);
			date.setMinutes(0);
			date.setSeconds(0);
			date.setMilliseconds(0);
			if (parts.length === format.parts.length) {
				var year = date.getFullYear(), day = date.getDate(), month = date.getMonth();
				for (var i=0, cnt = format.parts.length; i < cnt; i++) {
					val = parseInt(parts[i], 10)||1;
					switch(format.parts[i]) {
						case 'dd':
						case 'd':
							day = val;
							date.setDate(val);
							break;
						case 'mm':
						case 'm':
							month = val - 1;
							date.setMonth(val - 1);
							break;
						case 'yy':
							year = 2000 + val;
							date.setFullYear(2000 + val);
							break;
						case 'yyyy':
							year = val;
							date.setFullYear(val);
							break;
					}
				}
				date = new Date(year, month, day, 0 ,0 ,0);
			}
			return date;
		},
		formatDate: function(date, format){
			var val = {
				d: date.getDate(),
				m: date.getMonth() + 1,
				yy: date.getFullYear().toString().substring(2),
				yyyy: date.getFullYear()
			};
			val.dd = (val.d < 10 ? '0' : '') + val.d;
			val.mm = (val.m < 10 ? '0' : '') + val.m;
			var date = [];
			for (var i=0, cnt = format.parts.length; i < cnt; i++) {
				date.push(val[format.parts[i]]);
			}
			return date.join(format.separator);
		},
		headTemplate: '<thead>'+
							'<tr>'+
								'<th class="prev">&lsaquo;</th>'+
								'<th colspan="5" class="switch"></th>'+
								'<th class="next">&rsaquo;</th>'+
							'</tr>'+
						'</thead>',
		contTemplate: '<tbody><tr><td colspan="7"></td></tr></tbody>'
	};
	DPGlobal.template = '<div class="datepicker dropdown-menu">'+
							'<div class="datepicker-days">'+
								'<table class=" table-condensed">'+
									DPGlobal.headTemplate+
									'<tbody></tbody>'+
								'</table>'+
							'</div>'+
							'<div class="datepicker-months">'+
								'<table class="table-condensed">'+
									DPGlobal.headTemplate+
									DPGlobal.contTemplate+
								'</table>'+
							'</div>'+
							'<div class="datepicker-years">'+
								'<table class="table-condensed">'+
									DPGlobal.headTemplate+
									DPGlobal.contTemplate+
								'</table>'+
							'</div>'+
						'</div>';

}( window.jQuery );
