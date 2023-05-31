class Table {
    constructor(options = {}) {
        this.data = options.data || [];
        this.headersList = options.headers || [];
        this.headerColumnMap = options.headerColumnMap || {};
        this.props = options.props || [];
        this.numberOfHeaderRows = this.headersList.length;
    }

    renderTable() {
        let html = this.setElementProps('table');
        html += this.prepareHeader()
        html += this.prepareBody()
        html += '</table>';
        return html;
    }

    setElementProps(element, propsLookup=null, generalLookup=null) {
        let attributes = ''
        let properties = this.props?.[propsLookup] || this.props?.[generalLookup] || this.props?.[element]
        properties?.forEach(obj => attributes += `${obj?.key}="${obj?.value}" `)
        return attributes ? `<${element} ${attributes}>` : `<${element}>`
    }

    prepareHeader() {
        let html = '';
        html +=  this.setElementProps('thead');

        this.headersList?.forEach((columns, tr) => {
            html += this.setElementProps('tr', `headerRow${tr+1}`)
            columns.forEach((column, th) => {
                html += `${this.setElementProps('th', `headerRow${tr+1}th${th+1}`)}${column}</th>`;
            })
            html += '</tr>';
        });

        html += '</thead>';
        return html;
    }

    prepareBody() {
        const tableData = this.data;
        let html = '';
        html += this.setElementProps('tbody');

        tableData.forEach((row, i) => {
            html += this.setElementProps('tr', `bodyRow${i+1}`, 'red');

            this.headersList[this.headersList.length - 1].forEach(column => {
                html += `
                ${this.setElementProps('td')}
                ${row[this.headerColumnMap[column] || column]}
                </td>`;
            });

            html += '</tr>';
        });

        html += '</tbody>';
        return html
    }
}

// Example Usage
const table = new Table({
    data: [
        { name: 'John', age: 25, city: 'New York' },
        { name: 'Jane', age: 30, city: 'London' },
        { name: 'Bob', age: 35, city: 'Paris' }
    ],
    headers: [['','Person Table', ''], ['Person Name', 'Age', 'City']],
    headerColumnMap: {'Person Name': 'name', 'Age': 'age', 'City': 'city'},
    props: {
        table: [
            {key: 'id', value: 'some-table'}, 
            {key: 'class', value: 'table table-dark table-bg-dark'}
        ]
    }
    
}).renderTable();

document.body.innerHTML = table;
