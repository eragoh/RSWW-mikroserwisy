export default{
    name: 'Tours',
    props: ['description', 'page'],
    components: {},
    data() {
    return {
        tours: [],
        countries: [],
        filter: '',
        formData: {
            country: '',
            start_date: '',
            return_date: '',
            adults: 0,
            children: 0
        },
        showform: false
    }
},
    methods: {
        load: async function(){
            const url = '/gettours?page=' + this.page;
            this.tours = await (await fetch(url)).json();

            this.countries = await (await fetch('/getcountries/')).json();
        },
        redirectToTour(url) {
            window.location.href = url;
        },
        redirectToReservation(url) {
            window.location.href = url + '/buy/';
        },
        async submitForm() {
            const url = `/gettoursparameters?page=${this.page}&country=${this.formData.country}&start_date=${this.formData.start_date}&return_date=${this.formData.return_date}&adults=${this.formData.adults}&children=${this.formData.children}`;
            try{
                var response = await (await fetch(url)).json();
                this.tours = response;
            }catch(error){
                this.tours = null;
            }
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
        },
        showformFunction: function() {
            var button = document.getElementById("showformButton");
            if(this.showform){
                button.innerText = "Pokaż opcje wyszukiwania";
            }else{
                button.innerText = "Schowaj opcje wyszukiwania";
            }
            this.showform = !this.showform;
        }
    },
    computed: {},
    mounted() {
        this.load();
    },
    template: /*html*/`

    <button class="btn btn-primary mb-2" id="showformButton" @click="showformFunction()">Pokaż opcje wyszukiwania</button>

    <form v-if="showform" @submit.prevent="submitForm">
        <div class="form-group">
            <label for="country">Kraj docelowy</label>
            <select class="form-control" id="country" name="country" v-model="formData.country" >
                <option></option>
                <option v-for="country in countries" :value="country">
                    {{country}}
                </option>
            </select>
        </div>
        <div class="form-group">
            <label for="start_date">Data rozpoczęcia podróży:</label>
            <input class="form-control" type="date" id="start_date" name="start_date" v-model="formData.start_date" >
        </div>
        <div class="form-group">
            <label for="return_date">Data powrotu:</label>
            <input class="form-control" type="date" id="return_date" name="return_date" v-model="formData.return_date" >
        </div>
        <div class="form-group">
            <label for="country">Liczba dorosłych</label>
            <select class="form-control" id="adults" name="adults" v-model="formData.adults" >
                <option v-for="index in 10" :key="index">
                    {{index}}
                </option>
            </select>
        </div>
        <div class="form-group">
            <label for="country">Liczba dzieci (do 18 lat)</label>
            <select class="form-control" id="children" name="children" v-model="formData.children" >
                <option v-for="index in 11" :key="index">
                    {{index - 1}}
                </option>
            </select>
        </div>
        <button type="submit" class="btn btn-primary mb-2" style="width: 100%; text-align: center;">Szukaj</button>
    </form>
        <h3 class="text-center mt-3">{{description}}</h3>

        <section style="background-color: #eee;">
        <div class="container py-5">

        
            <div class="row justify-content-center mb-3" v-if="tours" v-for="tour in tours">
            <div class="col-md-12 col-xl-10">
                <div class="card shadow-0 border rounded-3">
                <div class="card-body">
                    <div class="row">
                    <div class="col-md-12 col-lg-3 col-xl-3 mb-4 mb-lg-0">
                        <div class="bg-image hover-zoom ripple rounded ripple-surface">
                        <a :href="tour._id.$oid"><img :src="tour.img" class="w-100" /></a>
                        </div>
                    </div>
                    <div class="col-md-6 col-lg-6 col-xl-6">
                        <h5>
                            <i class="bi bi-house"></i> 
                            <a :href="tour._id.$oid" style="text-decoration: none;">&nbsp{{tour.hotel}}</a>
                        </h5>
                        <div class="d-flex flex-row">
                        <div class="text-danger mb-1 me-2" v-for="star in tour.score">
                            <i class="bi bi-star-fill"></i>                            
                        </div>
                        <div class="text-danger mb-1 me-2" v-for="star in 5 - tour.score">
                            <i class="bi bi-star"></i>                            
                        </div>
                        <span>
                            {{ tour.country }}{{ tour.city !== '' ? ', ' + tour.city : '' }}
                        </span>
                        </div>
                        <div class="mt-1 mb-0 text-muted small">
                            <i class="bi bi-calendar-range"></i> {{tour.start_date}} - {{tour.end_date}}<br />
                            <i class="bi bi-airplane"></i> {{tour.departure_location}}<br />
                            <div style="display: inline-flex; align-items: center;">
                                <i class="bi bi-houses"></i>
                                <div style="margin-left: 8px;" class="mb-2 text-muted small" v-html="roomsf(tour.room)"></div>
                            </div>
                        </div>
                        <p class="text-truncate mb-4 mb-md-0">
                        {{tour.description}}
                        </p>
                    </div>
                    <div class="col-md-6 col-lg-3 col-xl-3 border-sm-start-none border-start">
                        <div class="d-flex flex-row align-items-center mb-1">
                        <h4 class="mb-1 me-1">{{tour.price}}zł/os.</h4>
                        <span class="text-danger"><s>{{Math.round(1.2 * tour.price) + 0.99}}zł</s></span>
                        </div>
                        <h6 class="text-success">Dostępny</h6>
                        <div class="d-flex flex-column mt-4">
                        
                        <button @click="redirectToTour(tour._id.$oid)" data-mdb-button-init data-mdb-ripple-init class="btn btn-primary btn-sm" type="button">Dalej</button>
                        <button @click="redirectToReservation(tour._id.$oid)" data-mdb-button-init data-mdb-ripple-init class="btn btn-outline-primary btn-sm mt-2" type="button">
                            Kup teraz!
                        </button>
                        </div>
                    </div>
                    </div>
                </div>
                </div>
            </div>
            </div>
            <div v-else>
                😔 Brak dostępnych wycieczek o podanych parametrach. 😔
            </div>


        </div>
        </section>

    `
}