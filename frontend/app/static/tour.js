export default{
    name: 'Tour',
    components: {},
    data() {
        return {
            tour: null,
            rooms: '',
            activity: '',
            availableh: true
        }
    },
    methods: {
        get_activity: function(response){
            var n = response['State']['result'];
            if(n > 1){
                this.activity = 
                `<div class="card text-center">
                    <div class="card-header">
                        UWAGA!
                    </div>
                    <div class="card-body">
                        <h5 class="card-title">W tym momencie stronę przegląda `
                    + n +
                                    ` użytkowników!</h5>
                    </div>
                    <div class="card-footer text-muted">
                        Pospiesz się i zrób zakup, bo będą przed tobą!!!
                    </div>
                </div>`;
            }else{
                this.activity = '';
            }
        },
        load: async function(){
            const url = window.location.href + 'get/';
            this.tour = await (await fetch(url)).json();
            
            var rooms_table = await (await fetch(window.location.href + 'reserved_rooms/')).json();
            var dict = {
                'Standardowy' : true,
                'Apartament' : true,
                'Studio' : true,
                'Rodzinny' : true,
            };
            for(var r in rooms_table['results']){
                dict[rooms_table['results'][r]] = false;
            }

            if(this.tour.room.is_standard && dict['Standardowy']){
                this.rooms += '<span>Pokój standardowy</span>';
            }
            if(this.tour.room.is_apartment && dict['Apartament']){
                if(this.rooms !== ''){
                    this.rooms += '<span class="text-primary"> • </span>';
                }
                this.rooms += '<span>Apartament</span>';
            }
            if(this.tour.room.is_studio && dict['Studio']){
                if(this.rooms !== ''){
                    this.rooms += '<span class="text-primary"> • </span>';
                }
                this.rooms += '<span>Studio</span>';
            }
            if(this.tour.room.is_family && dict['Rodzinny']){
                if(this.rooms !== ''){
                    this.rooms += '<span class="text-primary"> • </span>';
                }
                this.rooms += '<span>Pokój rodzinny</span>';
            }
            if(this.rooms == ''){
                this.rooms = 'Brak wolnych pokoji.';
                this.availableh=false;
            }
            var response = await (await fetch(window.location.href + 'watch/')).json();
            this.get_activity(response);
        },
        redirectToReservation(url) {
            window.location.href += 'buy/';
        },
        leaving: async function(e){
            var response = await fetch(window.location.href + 'watch_end/');
        },
        leavingatall: async function(e){
            var response = await fetch(window.location.href + 'watch_end/');
        },
        async fetchWatch() {
            var response = await (await fetch(window.location.href + 'watch_check/')).json();
            this.get_activity(response);
        },

    },
    computed: {},
    mounted() {
        window.addEventListener('beforeunload', this.leaving);
        window.addEventListener('unload', this.leavingatall);
        this.load();
        setInterval(this.fetchWatch, 10000);
    },
    template: /*html*/`
    
    <div v-if="tour">
    <div class="my-3 p-3">
        <h2 class="display-5">{{ tour.country }}{{ tour.city !== '' ? ', ' + tour.city : '' }}</h2>
        <div v-html="activity"></div>
        <img :src="tour.img" alt="Hotel Image" style="max-width: 100%;">
        <p class="lead">{{ tour.description }}</p>
    </div>
    <div class="row">
        <div class="col-md-6">
            <h3>{{ tour.hotel }}</h3>
            <div class="d-flex flex-row">
                <div class="text-danger mb-1 me-2" v-for="star in tour.score">
                    <i class="bi bi-star-fill"></i>                            
                </div>
                <div class="text-danger mb-1 me-2" v-for="star in 5 - tour.score">
                    <i class="bi bi-star"></i>                            
                </div>
            </div>
            
            <div class="mb-2 text-muted small">
                <i class="bi bi-calendar-range"></i> {{tour.start_date}} - {{tour.end_date}}<br />
                <i class="bi bi-airplane"></i> {{tour.departure_location}}<br />
                <div style="display: inline-flex; align-items: center;">
                    <i class="bi bi-houses"></i>
                    <div style="margin-left: 8px;" class="mb-2 text-muted small" v-html="rooms"></div>
                </div>
            </div>
        </div>
        <div class="col-md-6">
            <div class="d-flex flex-row align-items-center mb-1">
                <h4 class="mb-1 me-1">{{tour.price}}zł/os.</h4>
                <span class="text-danger"><s>{{Math.round(1.2 * tour.price) + 0.99}}zł</s></span>
            </div>
            <div v-if="availableh">
                <h6 class="text-success">Dostępny</h6>
                <div class="d-flex flex-column mt-4">
                    <button @click="redirectToReservation(tour._id.$oid)" data-mdb-button-init data-mdb-ripple-init class="btn btn-outline-primary btn-sm mt-2" type="button">
                        Kup teraz!
                    </button>
                </div>
            </div>
            <div v-else>
                <h6 class="text-danger">Niedostępny</h6>
                <div class="d-flex flex-column mt-4">
                    <button disabled @click="redirectToReservation(tour._id.$oid)" data-mdb-button-init data-mdb-ripple-init class="btn btn-outline-primary btn-sm mt-2" type="button">
                        Kup teraz!
                    </button>
                </div>
            </div>
            
        </div>
    </div>
</div>
<div v-else>
    <p>😔 Brak dostępnych wycieczek o podanych parametrach. 😔</p>
</div>

  `
}