const routes = [
  {
    path: '/',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      {
        path: '',
        component: () => import('pages/IndexPage.vue')
      },
      {
        path: 'agenda',
        component: () => import('pages/AgendaPage.vue')
      },
      {
        path: 'map',
        component: () => import('pages/MapPage.vue')
      },
      {
        path: 'info',
        component: () => import('pages/InfoPage.vue')
      },
      {
        path: 'explore',
        component: () => import('pages/ExplorePage.vue')
      }
    ]
  },
  {
    path: '/:catchAll(.*)*',
    redirect: '/'
  }
]

export default routes
