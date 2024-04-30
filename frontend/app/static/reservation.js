export default{
    name: 'Reservation',
    props: ['tourid'],
    components: {},
    data() {
        return {
            tour: null
        }
    },
    methods: {
        load: async function(){
            const url = '/tours/' + this.tourid + '/get/';
            this.tour = await (await fetch(url)).json();
        },
    },
    computed: {},
    mounted() {
        this.load();
    },
    template: /*html*/`
    <div v-if="tour">
        <div class="row">
            <div class="col-lg-4 mb-lg-0 mb-3">
                <div class="card p-3">
                    <div class="img-box">
                        <img src="https://www.freepnglogos.com/uploads/visa-logo-download-png-21.png" alt="">
                    </div>
                    <div class="number">
                        <label class="fw-bold" for="">**** **** **** 1060</label>
                    </div>
                    <div class="d-flex align-items-center justify-content-between">
                        <small><span class="fw-bold">Expiry date:</span><span>10/16</span></small>
                        <small><span class="fw-bold">Name:</span><span>ADMIN</span></small>
                    </div>
                </div>
            </div>
    
            <div>
                <div class="col-12 mt-4">
                    <div class="card p-3">
                        <p class="mb-0 fw-bold h4">Przejdź do płatności</p>
                    </div>
                </div>

            <div class="col-12">
                <div class="card p-3">
                    <div class="card-body border p-0">
                        <p>
                            <a class="btn btn-primary p-2 w-100 h-100 d-flex align-items-center justify-content-between"
                                data-bs-toggle="collapse" href="#collapseExample" role="button" aria-expanded="true"
                                aria-controls="collapseExample">
                                <span class="fw-bold">Karta kredytowa</span>
                                <span class="">
                                    <span class="fab fa-cc-amex"></span>
                                    <span class="fab fa-cc-mastercard"></span>
                                    <span class="fab fa-cc-discover"></span>
                                </span>
                            </a>
                        </p>
                        <div class="collapse show p-3 pt-0" id="collapseExample">
                            <div class="row">
                                <div class="col-lg-5 mb-lg-0 mb-3">
                                    <p class="h4 mb-0">Podsumowanie</p>
                                    <p class="mb-0"><span class="fw-bold">Produkt: </span><span class="c-green"> {{tour.hotel}}</span></p>
                                    <p class="mb-0"><span class="fw-bold">Miejsce: </span><span class="c-green"> {{ tour.country }}{{ tour.city !== '' ? ', ' + tour.city : '' }}</span></p>
                                    <p class="mb-0">
                                        <span class="fw-bold">Price:</span>
                                        <span class="c-green">:$452.90</span>
                                    </p>
                                    <p class="mb-0 text-truncate">
                                        {{tour.description}}
                                    </p>
                                </div>
                                <div class="col-lg-7">
                                    <form class="form" method="post">
                                        <div class="row">
                                            <div class="col-12">
                                                <div class="form__div">
                                                    <input required type="text" class="form-control" placeholder=" " name="card_number">
                                                    <label for="" class="form__label">Numer karty</label>
                                                </div>
                                            </div>

                                            <div class="col-6">
                                                <div class="form__div">
                                                    <input required type="text" class="form-control" placeholder=" " name="card_expiration_date">
                                                    <label for="" class="form__label">MM / yy</label>
                                                </div>
                                            </div>

                                            <div class="col-6">
                                                <div class="form__div">
                                                    <input required type="password" class="form-control" placeholder=" " name="ccv_code">
                                                    <label for="" class="form__label">kod cvv</label>
                                                </div>
                                            </div>
                                            <div class="col-12">
                                                <div class="form__div">
                                                    <input type="text" class="form-control" placeholder=" " name="card_number">
                                                    <label for="" class="form__label">Nazwa karty</label>
                                                </div>
                                            </div>
                                        </div>
                                        <div class="col-12">
                                            <button class="btn btn-primary payment" type="submit">
                                                Zapłać
                                            </button>
                                        </div>
                                    </form>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            


        </div>
    </div>
    </div>

    <div v-else>
        <p>😔 Wystąpił błąd ex1024865. Sprawdź ponownie swoje dane. 😔</p>
    </div>
<br />
  `
}