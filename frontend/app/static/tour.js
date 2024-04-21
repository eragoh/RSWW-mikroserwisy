export default{
    name: 'Tour',
    components: {},
    data() {
    return {
        tour: null
    }
},
    methods: {
        load: async function(){
            const url = window.location.href + '/get/';
            this.tour = await (await fetch(url)).json();
        },
        roomsf: function(t){
            var rooms = ''
            if(t.is_standard){
                rooms += '<span>Pokój standardowy</span>';
            }
            if(t.is_family){
                if(rooms !== ''){
                    rooms += '<span class="text-primary"> • </span>';
                }
                rooms += '<span>Pokój rodzinny</span>';
            }
            if(t.is_apartment){
                if(rooms !== ''){
                    rooms += '<span class="text-primary"> • </span>';
                }
                rooms += '<span>Apartament</span>';
            }
            if(t.is_studio){
                if(rooms !== ''){
                    rooms += '<span class="text-primary"> • </span>';
                }
                rooms += '<span>Studio</span>';
            }
            return rooms;
        }
        
    },
    computed: {},
    mounted() {
        this.load();
    },
    template: /*html*/`
    
    <div v-if="tour">
    <div class="my-3 p-3">
        <h2 class="display-5">{{ tour.country }}{{ tour.city !== '' ? ', ' + tour.city : '' }}</h2>
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
                    <div style="margin-left: 8px;" class="mb-2 text-muted small" v-html="roomsf(tour.room)"></div>
                </div>
            </div>
        </div>
        <div class="col-md-6">
            <div class="d-flex flex-row align-items-center mb-1">
                <h4 class="mb-1 me-1">{{tour.price}}zł/os.</h4>
                <span class="text-danger"><s>{{1.2 * tour.price}}zł</s></span>
            </div>
            <h6 class="text-success">Dostępny</h6>
            <div class="d-flex flex-column mt-4">
                <button data-mdb-button-init data-mdb-ripple-init class="btn btn-outline-primary btn-sm mt-2" type="button">
                    Kup teraz!
                </button>
            </div>
        </div>
    </div>
</div>
<div v-else>
    <p>Loading...</p>
</div>

  `
}