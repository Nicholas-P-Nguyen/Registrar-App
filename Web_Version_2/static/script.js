'use strict';

//----------------------------------------------------------------------
// Below are functions to get the course details
//----------------------------------------------------------------------

// getDetails is triggered when user clicks on a button that specifies 
// what class id the user clicked, passing in as argument the classid 
let requestDetails = null;
function getResultsDetails(classid) {
    function handleResponse(details) {
        let success = details[0];

        if (success) {
            let html = convertDetailsToHtml(details[1]);
            $('#classDetailsModalBody').html(html);
            $('#detailsModal').modal('show');
        }
        else {
            let error = details[1];
            alert(error);
        }
    }

    function convertDetailsToHtml(details) {
        let template = `
        <h2>Class Details</h2>
        <table class="table table-striped" id="classDetailsTable">
        <tr>
            <td><strong>Class Id</strong></td>
            <td>{{details.classid}}</td>
        </tr>
        <tr>
            <td><strong>Days</strong></td>
            <td>{{details.days}}</td>
        </tr>
        <tr>
            <td><strong>Start time</strong></td>
            <td>{{details.starttime}}</td>
        </tr>
        <tr>
            <td><strong>End time</strong></td>
            <td>{{details.endtime}}</td>
        </tr>
        <tr>
            <td><strong>Building</strong></td>
            <td>{{details.bldg}}</td>
        </tr>
        <tr>
            <td><strong>Room</strong></td>
            <td>{{details.roomnum}}</td>
        </tr>
        </table>

        <h2>Course Details</h2>
        <table class="table table-striped" id="courseDetailsTable">
        <tr>
            <td><strong>Course Id</strong></td>
            <td>{{details.courseid}}</td>
        </tr>
        {{#details.deptcoursenums}}
            <tr>
                <td><strong>Dept and Number</strong></td>
                <td>{{dept}} {{coursenum}}</td>
            </tr>
        {{/details.deptcoursenums}}
        <tr>
            <td><strong>Area</strong></td>
            <td>{{details.area}}</td>
        </tr>
        <tr>
            <td><strong>Title</strong></td>
            <td>{{details.title}}</td>
        </tr>
        <tr>
            <td><strong>Description</strong></td>
            <td>{{details.descrip}}</td>
        </tr>
        <tr>
            <td><strong>Prerequisites</strong></td>
            <td>{{details.prereqs}}
        {{#details.profnames}}
            <tr>
                <td><strong>Professor</strong></td>
                <td>{{.}}</td>
            </tr>
        {{/details.profnames}}
        </table>
        `;
        let map = {details: details};
        let html = Mustache.render(template, map);
        return html
    }
    let encodedClassid = encodeURIComponent(classid)

    let url = '/regdetails?classid=' + encodedClassid

    if (requestDetails !== null) {
        requestDetails.abort();
    }

    let requestData = {
        type: 'GET',
        url: url,
        success: handleResponse,
        error: handleError
    };
    request = $.ajax(requestData)

}

//----------------------------------------------------------------------
// Below are functions to get the course overviews
//----------------------------------------------------------------------

function handleResponse(overviews) {
    let success = overviews[0]

    if (success) {
        let html = convertOverviewsToHtml(overviews[1])
        $('#resultOverviews').html(html)
    }
    else {
        let error = overviews[1];
        alert(error);
    }
}

function convertOverviewsToHtml(overviews) {
    let template = ` 
    <table class="table table-striped" id="overviewsTable">
        <thead>
            <tr>
                <td><strong>ClassId</strong></td>
                <td><strong>Dept</strong></td>
                <td><strong>Num</strong></td>
                <td><strong>Area</strong></td>
                <td><strong>Title</strong></td>
            </tr>
        </thead>
        <tbody>
            {{#overviews}}
            <tr>
                <td><button id="button{{classid}}" onclick="getResultsDetails({{classid}})">{{classid}}</button></td>
                <td>{{dept}}</td>
                <td>{{coursenum}}</td>
                <td>{{area}}</td>
                <td>{{title}}</td>
            </tr>
            {{/overviews}}
        </tbody>
    </table>
    `;
    let map = {overviews: overviews};
    let html = Mustache.render(template, map);
    return html
}

function handleError(request) {
    if (request.statusText !== 'abort') {
        alert('Error: Failed to fetch data from server')
    }

}

let request = null;
function getOverviews() {
    let dept = $('#deptInput').val();
    let encodedDept = encodeURIComponent(dept);

    let coursenum = $('#coursenumInput').val();
    let encodedCoursenum = encodeURIComponent(coursenum);

    let area = $('#areaInput').val();
    let encodedArea = encodeURIComponent(area);

    let title = $('#titleInput').val();
    let encodedTitle = encodeURIComponent(title);

    let url = '/regoverviews?dept=' + encodedDept + '&coursenum=' + encodedCoursenum + '&area=' + encodedArea + '&title=' + encodedTitle

    if (request !== null) {
        request.abort();
    }
    let requestData = {
        type: 'GET',
        url: url,
        success: handleResponse,
        error: handleError
    };
    request = $.ajax(requestData)
}

let timer = null;
function debouncedResults() {
    clearTimeout(timer);
    timer = window.setTimeout(getOverviews, 500)
}

function setup() {
    $('#deptInput').on('input', debouncedResults);
    $('#coursenumInput').on('input', debouncedResults);
    $('#areaInput').on('input', debouncedResults);
    $('#titleInput').on('input', debouncedResults);
    
    getOverviews();

}
$('document').ready(setup);