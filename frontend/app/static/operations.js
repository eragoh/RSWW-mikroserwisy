export default{
    name: 'Operations',
    components: {},
    data() {
        return {
            operations: null,
        }
    },
    methods: {
        load: async function(){
            try {
                let response = await fetch('/operations_json/');
                let data = await response.json();
                if (typeof data.operations === 'string') {
                    this.operations = JSON.parse(data.operations);
                } else {
                    this.operations = data.operations;
                }
            } catch (error) {
                console.error("Error loading operations:", error);
            }
        },
    },
    computed: {},
    mounted() {
        this.load();
    },
    template: /*html*/`
        <div>
            <table v-if="operations" class="table">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Wycieczka</th>
                        <th>standardowy</th>
                        <th>rodzinny</th>
                        <th>apartament</th>
                        <th>studio</th>
                        <th>cena</th>
                        <th>dorośli</th>
                        <th>ch3</th>
                        <th>ch10</th>
                        <th>ch18</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="operation in operations" :key="operation[0]">
                        <th scope="row">{{ operation[0] }}</th>
                        <td>{{ operation[1] === -1 ? '-' : operation[1] }}</td>
                        <td>{{ operation[2] === -1 ? '-' : operation[2] }}</td>
                        <td>{{ operation[3] === -1 ? '-' : operation[3] }}</td>
                        <td>{{ operation[4] === -1 ? '-' : operation[4] }}</td>
                        <td>{{ operation[5] === -1 ? '-' : operation[5] }}</td>
                        <td>{{ operation[6] === -1 ? '-' : operation[6] }}</td>
                        <td>{{ operation[7] === -1 ? '-' : operation[7] }}</td>
                        <td>{{ operation[8] === -1 ? '-' : operation[8] }}</td>
                        <td>{{ operation[9] === -1 ? '-' : operation[9] }}</td>
                        <td>{{ operation[10] === -1 ? '-' : operation[10] }}</td>
                    </tr>
                </tbody>
            </table>
            <p v-else>Loading operations...</p>
        </div>
    `
}