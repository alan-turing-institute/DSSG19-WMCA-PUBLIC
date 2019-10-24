#!/bin/bash

PROJECT="DSSG19-WMCA"
PROJECT_HOME="$( cd "$( dirname "$0" )" && pwd )"

cd "$PROJECT_HOME"


function help_menu () {
cat << EOF 
Usage: ${0} {up|down|build|rebuild|run|logs|status|clean}

OPTIONS:
   -h|help             Show this message
   deploy              Deploy entire pipeline
   up                  Starts Food DB
   down                Stops Food DB
   build               Builds images (food_db and bastion)
   rebuild             Builds images (food_db and bastion) ignoring if they already exists
   -l|logs             Shows container's logs
   status              Shows status of the containers
   -d|clean            Removes containers, images, volumes, netrowrks

INFRASTRUCTURE:
    Run ETL + pipeline + visualization:
        $ ./deploy.sh deploy -mode replace
        $ ./deploy.sh deploy -mode append
   Build the infrastructure:
        $ ./deploy.sh up
   Check the status of the containers:
        $ ./deploy.sh status
   Stop the infrastructure:
        $ ./deploy.sh down
   Destroy all the resources related to the project:
        $ ./deploy.sh clean
   View the infrastructure logs:
        $ ./deploy.sh -l

EOF
}

function start_infrastructure () {
    docker-compose up "${@}"
}

function stop_infrastructure () {
    docker stop "${@}"
}

function remove_infrastructure () {
    docker rm "${@}"
}

function run_pipeline() {
    docker-compose run pipeline -c "${@}"
}

function build_images () {
    docker-compose build "${@}"
}

function destroy () {
    docker-compose down --rmi all --remove-orphans --volumes
}

function infrastructure_logs () {
    docker-compose logs -f -t
}

function status () {
    docker-compose ps
}

function deploy () {
    start_infrastructure -d pipeline load-balancer 
    status
    echo "Running ETL"
    run_pipeline "import run_etl; run_etl.run()"
    echo "Building models in mode '$MODE' "
    run_pipeline "import run_model; run_model.run(mode='$MODE')"
    echo "Upping dashboard"
    start_infrastructure -d dashboard
    echo "Removing infrastructure"
    stop_infrastructure $(docker ps -a | grep -e otp -e load-balancer | awk '{print $1}')
    remove_infrastructure $(docker ps -a | grep -e otp -e load-balancer | awk '{print $1}')
    status
}


if [[ $# -eq 0 ]] ; then
    help_menu
    exit 0
fi

case "$1" in 
    deploy)
        if [[ $# -ne 3 ]]; then
            echo "ERROR: must specify -mode flag"
        else
            MODE=$3
            deploy
        fi
        shift
        ;;
    up)
        start_infrastructure
        shift
        ;;
    down)
        stop_infrastructure
        shift
        ;;
    build)
        build_images
        shift
        ;;
    rebuild)
        build_images --no-cache
        shift
        ;;
    -d|clean)
        destroy
        shift
        ;;
    -l|logs)
        infrastructure_logs
        shift
        ;;
    status)
        status
        shift
        ;;
    -h|--help)
        help_menu
        shift
        ;;
    *)
        echo "${1} is not a valid flag, try running: ${0} --help"
        shift
        ;;

esac
shift

