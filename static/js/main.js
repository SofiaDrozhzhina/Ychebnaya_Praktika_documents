// static/js/main.js
$(function() {
  // --- utility ---
  function formatDate(iso) {
    if (!iso) return '';
    const d = new Date(iso);
    const dd = String(d.getDate()).padStart(2,'0');
    const mm = String(d.getMonth()+1).padStart(2,'0');
    const yyyy = d.getFullYear();
    return `${dd}.${mm}.${yyyy}`;
  }

  function renderGrade(grade) {
    if (!grade || grade === "") return `<span class="grade-pill grade-na">Не оценено</span>`;
    if (grade === '5') return `<span class="grade-pill grade-5">5</span>`;
    if (grade === '4') return `<span class="grade-pill grade-4">4</span>`;
    if (grade === '3') return `<span class="grade-pill grade-3">3</span>`;
    if (grade === '2') return `<span class="grade-pill grade-2">2</span>`;
    return `<span class="grade-pill grade-na">${grade}</span>`;
  }

  // --- LOAD initial lists for selects (students, courses) ---
  function loadStudentsForSelect(selectId) {
    $.getJSON('/api/students').done(function(data) {
      const sel = $(selectId);
      sel.empty();
      data.forEach(s => sel.append(`<option value="${s.id}">${s.fio}</option>`));
    });
  }
  function loadCoursesForSelect(selectId) {
    $.getJSON('/api/courses').done(function(data) {
      const sel = $(selectId);
      sel.empty();
      sel.append(`<option value="">-- выберите --</option>`);
      data.forEach(c => sel.append(`<option value="${c.id}">${c.name}</option>`));
    });
  }

  // Fill filters on main page
  function fillCourseFilter() {
    $.getJSON('/api/courses').done(function(data) {
      const sel = $('#records-course-filter');
      sel.empty();
      sel.append(`<option value="">Все курсы</option>`);
      data.forEach(c => sel.append(`<option value="${c.id}">${c.name}</option>`));
    });
  }

  // fill teachers filter on courses page
  function fillTeachersFilter() {
    $.getJSON('/api/courses').done(function(data) {
      const teacherSet = new Set();
      data.forEach(c => { if (c.teacher) teacherSet.add(c.teacher) });
      const sel = $('#courses-teacher-filter');
      sel.empty();
      sel.append(`<option value="">Все преподаватели</option>`);
      [...teacherSet].forEach(t => sel.append(`<option value="${t}">${t}</option>`));
    });
  }

  // --- Records table ---
  function loadRecords(params={}) {
    $.getJSON('/api/records', params).done(function(data) {
      const tbody = $('#records-table tbody');
      tbody.empty();
      data.forEach(r => {
        const row = `<tr data-id="${r.id}">
          <td>${r.student_fio || ''}</td>
          <td>${r.course_name || ''}</td>
          <td>${formatDate(r.date)}</td>
          <td>${renderGrade(r.grade)}</td>
        </tr>`;
        tbody.append(row);
      });
    });
  }

  // --- Students table ---
  function loadStudents(params={}) {
    $.getJSON('/api/students', params).done(function(data) {
      const tbody = $('#students-table tbody');
      tbody.empty();
      data.forEach(s => {
        const row = `<tr data-id="${s.id}"><td>${s.fio}</td><td>${formatDate(s.date_of_birth)}</td><td>${s.phone || ''}</td></tr>`;
        tbody.append(row);
      });
    });
  }

  // --- Courses table ---
  function loadCourses(params={}) {
    $.getJSON('/api/courses', params).done(function(data) {
      const tbody = $('#courses-table tbody');
      tbody.empty();
      data.forEach(c => {
        const row = `<tr data-id="${c.id}"><td>${c.name}</td><td>${c.description || ''}</td><td>${c.teacher || ''}</td></tr>`;
        tbody.append(row);
      });
    });
  }

  // --- Add/Edit page: list of chosen table on right ---
  function loadAddList(table) {
    const thead = $('#add-list-table thead');
    const tbody = $('#add-list-table tbody');
    thead.empty(); tbody.empty();
    if (table==='students') {
      thead.html('<tr><th>ФИО</th><th>Дата рождения</th><th>Телефон</th></tr>');
      $.getJSON('/api/students').done(function(data){
        data.forEach(s => tbody.append(`<tr data-id="${s.id}"><td>${s.fio}</td><td>${formatDate(s.date_of_birth)}</td><td>${s.phone||''}</td></tr>`));
      });
    } else if (table==='courses') {
      thead.html('<tr><th>Название</th><th>Описание</th><th>Преподаватель</th></tr>');
      $.getJSON('/api/courses').done(function(data){
        data.forEach(c => tbody.append(`<tr data-id="${c.id}"><td>${c.name}</td><td>${c.description||''}</td><td>${c.teacher||''}</td></tr>`));
      });
    } else {
      thead.html('<tr><th>Студент</th><th>Курс</th><th>Дата</th><th>Оценка</th></tr>');
      $.getJSON('/api/records').done(function(data){
        data.forEach(r => tbody.append(`<tr data-id="${r.id}"><td>${r.student_fio||''}</td><td>${r.course_name||''}</td><td>${formatDate(r.date)}</td><td>${r.grade||''}</td></tr>`));
      });
    }
  }

  // --- Delete list ---
  function loadDeleteList(table) {
    const thead = $('#delete-list-table thead');
    const tbody = $('#delete-list-table tbody');
    thead.empty(); tbody.empty();
    if (table==='students') {
      thead.html('<tr><th>ФИО</th><th>Дата рождения</th></tr>');
      $.getJSON('/api/students').done(function(data){
        data.forEach(s => tbody.append(`<tr data-id="${s.id}"><td>${s.fio}</td><td>${formatDate(s.date_of_birth)}</td></tr>`));
      });
    } else if (table==='courses') {
      thead.html('<tr><th>Название</th><th>Преподаватель</th></tr>');
      $.getJSON('/api/courses').done(function(data){
        data.forEach(c => tbody.append(`<tr data-id="${c.id}"><td>${c.name}</td><td>${c.teacher||''}</td></tr>`));
      });
    } else {
      thead.html('<tr><th>Студент</th><th>Курс</th><th>Дата</th></tr>');
      $.getJSON('/api/records').done(function(data){
        data.forEach(r => tbody.append(`<tr data-id="${r.id}"><td>${r.student_fio||''}</td><td>${r.course_name||''}</td><td>${formatDate(r.date)}</td></tr>`));
      });
    }
  }

  // --- Events wiring ---
  // Main page controls
  $('#records-search').on('input', function() {
    const q = $(this).val();
    const course = $('#records-course-filter').val();
    const sort = $('.btn-group #sort-default').hasClass('active') ? 'default' : ($('#sort-asc').hasClass('active') ? 'asc' : 'desc');
    loadRecords({ q, course_id: course, sort });
  });
  $('#records-course-filter').on('change', function() {
    $('#records-search').trigger('input');
  });

  $('#sort-default').on('click', function(){ $('.btn-group .btn').removeClass('active'); $(this).addClass('active'); $('#records-search').trigger('input'); });
  $('#sort-asc').on('click', function(){ $('.btn-group .btn').removeClass('active'); $(this).addClass('active'); $('#records-search').trigger('input'); });
  $('#sort-desc').on('click', function(){ $('.btn-group .btn').removeClass('active'); $(this).addClass('active'); $('#records-search').trigger('input'); });

  // Students page
  $('#students-search').on('input', function() {
    const q = $(this).val();
    const sort = $('#students-sort-asc').hasClass('active') ? 'asc' : ($('#students-sort-desc').hasClass('active') ? 'desc' : 'default');
    loadStudents({ q, sort });
  });
  $('#students-sort-default').on('click', function(){ $('.btn-group .btn').removeClass('active'); $(this).addClass('active'); $('#students-search').trigger('input'); });
  $('#students-sort-asc').on('click', function(){ $('.btn-group .btn').removeClass('active'); $(this).addClass('active'); $('#students-search').trigger('input'); });
  $('#students-sort-desc').on('click', function(){ $('.btn-group .btn').removeClass('active'); $(this).addClass('active'); $('#students-search').trigger('input'); });

  // Courses page
  $('#courses-search').on('input', function() {
    const q = $(this).val();
    const teacher = $('#courses-teacher-filter').val();
    loadCourses({ q, teacher });
  });
  $('#courses-teacher-filter').on('change', function(){ $('#courses-search').trigger('input'); });

  // Add/Edit page: switching forms
  $('#add-table-select').on('change', function(){
    const val = $(this).val();
    $('.add-form').addClass('d-none');
    $(`#form-${val}`).removeClass('d-none');
    loadAddList(val);
    loadStudentsForSelect('#record-student');
    loadCoursesForSelect('#record-course');
  });
  // Delete page switch
  $('#delete-table-select').on('change', function(){
    const val = $(this).val();
    loadDeleteList(val);
    $('#delete-info').text('Выберите запись справа для удаления');
    $('#delete-confirm-btn').addClass('d-none').data('id','');
  });

  // Click handler on add-list-table rows to populate form for editing
  $('#add-list-table tbody').on('click', 'tr', function(){
    const table = $('#add-table-select').val();
    const id = $(this).data('id');
    if (!id) return;
    // fetch entity and populate form
    if (table === 'students') {
      $.getJSON(`/api/students`).done(function(data){
        const s = data.find(x => x.id === id);
        if (!s) return;
        $('#student-fio').val(s.fio);
        $('#student-dob').val(s.date_of_birth);
        $('#student-phone').val(s.phone);
        $('#student-add-btn').addClass('d-none');
        $('#student-edit-btn').removeClass('d-none').data('id', id);
      });
    } else if (table === 'courses') {
      $.getJSON('/api/courses').done(function(data){
        const c = data.find(x => x.id === id);
        if (!c) return;
        $('#course-name').val(c.name);
        $('#course-desc').val(c.description);
        $('#course-teacher').val(c.teacher);
        $('#course-add-btn').addClass('d-none');
        $('#course-edit-btn').removeClass('d-none').data('id', id);
      });
    } else {
      $.getJSON('/api/records').done(function(data){
        const r = data.find(x => x.id === id);
        if (!r) return;
        $('#record-student').val(r.id_student);
        $('#record-course').val(r.course_id);
        $('#record-date').val(r.date);
        $('#record-grade').val(r.grade || '');
        $('#record-add-btn').addClass('d-none');
        $('#record-edit-btn').removeClass('d-none').data('id', id);
      });
    }
  });

  // Delete page click selection
  $('#delete-list-table tbody').on('click', 'tr', function(){
    const id = $(this).data('id');
    const table = $('#delete-table-select').val();
    $('#delete-list-table tbody tr').removeClass('table-active');
    $(this).addClass('table-active');
    $('#delete-confirm-btn').removeClass('d-none').data('id', id).data('table', table);
    // Show info about chosen
    $('#delete-info').text(`Выбрана запись id=${id} (таблица: ${table})`);
  });

  // Confirm delete
  $('#delete-confirm-btn').on('click', function(){
    const id = $(this).data('id');
    const table = $(this).data('table');
    let url = '/api/';
    if (table === 'students') url += `students/${id}`;
    else if (table === 'courses') url += `courses/${id}`;
    else url += `records/${id}`;

    $.ajax({ url, type: 'DELETE' }).done(function(){
      alert('Удалено');
      loadDeleteList(table);
    }).fail(function(err){ alert('Ошибка удаления'); });
  });

  // Add handlers
  $('#student-add-btn').on('click', function(){
    const payload = {
      fio: $('#student-fio').val().trim(),
      date_of_birth: $('#student-dob').val(),
      phone: $('#student-phone').val().trim()
    };
    $.ajax({ url:'/api/students', type:'POST', contentType:'application/json', data: JSON.stringify(payload)})
    .done(function(){ alert('Студент добавлен'); loadAddList('students'); loadStudents(); })
    .fail(function(){ alert('Ошибка добавления'); });
  });
  $('#course-add-btn').on('click', function(){
    const payload = {
      name: $('#course-name').val().trim(),
      description: $('#course-desc').val().trim(),
      teacher: $('#course-teacher').val().trim()
    };
    $.ajax({ url:'/api/courses', type:'POST', contentType:'application/json', data: JSON.stringify(payload)})
    .done(function(){ alert('Курс добавлен'); loadAddList('courses'); fillCourseFilter(); fillTeachersFilter(); })
    .fail(function(){ alert('Ошибка добавления'); });
  });
  $('#record-add-btn').on('click', function(){
    const payload = {
      id_student: parseInt($('#record-student').val()),
      course_id: parseInt($('#record-course').val()),
      date: $('#record-date').val(),
      grade: $('#record-grade').val()
    };
    $.ajax({ url:'/api/records', type:'POST', contentType:'application/json', data: JSON.stringify(payload)})
    .done(function(){ alert('Запись добавлена'); loadAddList('records'); loadRecords(); })
    .fail(function(){ alert('Ошибка добавления'); });
  });

  // Edit handlers
  $('#student-edit-btn').on('click', function(){
    const id = $(this).data('id');
    const payload = { fio: $('#student-fio').val().trim(), date_of_birth: $('#student-dob').val(), phone: $('#student-phone').val().trim() };
    $.ajax({ url:`/api/students/${id}`, type:'PUT', contentType:'application/json', data: JSON.stringify(payload) })
    .done(function(){ alert('Сохранено'); loadAddList('students'); loadStudents(); $('#student-edit-btn').addClass('d-none'); $('#student-add-btn').removeClass('d-none'); })
    .fail(function(){ alert('Ошибка сохранения'); });
  });
  $('#course-edit-btn').on('click', function(){
    const id = $(this).data('id');
    const payload = { name: $('#course-name').val().trim(), description: $('#course-desc').val().trim(), teacher: $('#course-teacher').val().trim() };
    $.ajax({ url:`/api/courses/${id}`, type:'PUT', contentType:'application/json', data: JSON.stringify(payload) })
    .done(function(){ alert('Сохранено'); loadAddList('courses'); fillCourseFilter(); fillTeachersFilter(); $('#course-edit-btn').addClass('d-none'); $('#course-add-btn').removeClass('d-none'); })
    .fail(function(){ alert('Ошибка сохранения'); });
  });
  $('#record-edit-btn').on('click', function(){
    const id = $(this).data('id');
    const payload = { id_student: parseInt($('#record-student').val()), course_id: parseInt($('#record-course').val()), date: $('#record-date').val(), grade: $('#record-grade').val() };
    $.ajax({ url:`/api/records/${id}`, type:'PUT', contentType:'application/json', data: JSON.stringify(payload) })
    .done(function(){ alert('Сохранено'); loadAddList('records'); loadRecords(); $('#record-edit-btn').addClass('d-none'); $('#record-add-btn').removeClass('d-none'); })
    .fail(function(){ alert('Ошибка сохранения'); });
  });

  // Initialization on page load
  (function init() {
    fillCourseFilter();
    fillTeachersFilter();
    loadRecords();
    loadStudents();
    loadCourses();
    // If on add page, load students/courses selects and list
    if ($('#add-table-select').length) {
      $('#add-table-select').trigger('change');
      loadStudentsForSelect('#record-student');
      loadCoursesForSelect('#record-course');
    }
    if ($('#delete-table-select').length) {
      $('#delete-table-select').trigger('change');
    }
  })();

});
